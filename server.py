"""
ScamShield MCP server.
Exposes the scam checker as an MCP tool that Alexa+ calls over Streamable HTTP.
Run:  python server.py   ->  serves at http://127.0.0.1:8000/mcp
"""
from mcp.server.mcpserver import MCPServer
from check import check_message
from link_detector import analyze_link

mcp = MCPServer(
    name="ScamShield",
    instructions=(
        "Use ScamShield when a user is unsure whether a text, email, or message "
        "they received is a scam or phishing attempt. Pass the suspicious text to "
        "check_scam and relay the risk level and advice calmly. Never ask the user "
        "to share one-time passcodes, passwords, or full card numbers."
    ),
)


@mcp.tool(
    name="check_scam",
    description=(
        "Analyze a suspicious message, text, or email and return whether it is a "
        "scam or phishing attempt, with a risk level (SAFE, SUSPICIOUS, DANGEROUS) "
        "and the warning signs found. Use whenever someone asks if a message is a scam."
    ),
)

def check_scam(message: str) -> dict:
    """Check `message` for scam/phishing risk and return a verdict for Alexa+ to read."""
    result = check_message(message)
    return {
        "risk_level": result["risk_level"],
        "warning_signs": result["reasons"],
        "caught_by": result["caught_by"],
        "advice": _advice(result["risk_level"]),
    }

@mcp.tool(
    name="check_link",
    description=(
        "Analyze a single URL or link and return whether it is a phishing or scam "
        "link, with a risk level (SAFE, SUSPICIOUS, DANGEROUS) and the specific red "
        "flags found. Use when someone asks whether a link or website is safe."
    ),
)
def check_link(url: str) -> dict:
    """Check a URL for phishing/scam risk."""
    r = analyze_link(url)
    return {
        "risk_level": r["risk_level"],
        "warning_signs": r["signals"],
        "advice": _advice(r["risk_level"]),
    }


def _advice(level: str) -> str:
    if level == "DANGEROUS":
        return ("This looks like a scam. Do not reply, click links, call numbers in it, "
                "or share any codes, passwords, or payment. If it claims to be a company "
                "you use, contact them using a number from their official website.")
    if level == "SUSPICIOUS":
        return ("Be cautious - this shows warning signs. Verify the sender through an "
                "official channel before doing anything it asks.")
    return "No strong scam signs found, but stay alert and never share one-time codes."


if __name__ == "__main__":
    print("Starting ScamShield MCP server on http://127.0.0.1:8181/mcp ...")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8181)