# uawos_cli.py
import argparse
import sys

import uawos_agent_workforce
import uawos_integrations


def main():
    parser = argparse.ArgumentParser(description="UAWOS Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # register-agent
    reg_parser = subparsers.add_parser("register-agent", help="Onboard a new agent dynamically")
    reg_parser.add_argument("--name", required=True, help="Agent name")
    reg_parser.add_argument(
        "--class", dest="agent_class", required=True, help="Agent class (Orchestrator, Executor, etc.)"
    )
    reg_parser.add_argument("--capabilities", default="", help="Comma-separated capabilities list")

    # mcp-connect
    mcp_parser = subparsers.add_parser("mcp-connect", help="Establish an MCP connection for a third-party agent")
    mcp_parser.add_argument("--agent", required=True, help="Agent name or ID")
    mcp_parser.add_argument("--mcp-url", required=True, help="External MCP server url")

    args = parser.parse_args()

    if args.command == "register-agent":
        caps = [c.strip() for c in args.capabilities.split(",") if c.strip()]
        try:
            agent = uawos_agent_workforce.register_agent(
                name=args.name, agent_class=args.agent_class, capabilities=caps
            )
            print(f"SUCCESS: Agent '{args.name}' registered with ID {agent['id']}.")
        except Exception as e:
            print(f"ERROR: Failed to register agent: {e}")
            sys.exit(1)

    elif args.command == "mcp-connect":
        try:
            uawos_integrations.setup_mcp_agent_server(agent_id=args.agent, mcp_url=args.mcp_url)
            print(f"SUCCESS: MCP server connection established for '{args.agent}' to {args.mcp_url}.")
        except Exception as e:
            print(f"ERROR: Failed to connect MCP: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
