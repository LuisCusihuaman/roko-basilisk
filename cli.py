#!/usr/bin/env python3
"""
Interactive Roko's Basilisk CLI

An interactive command-line interface for the Basilisk evaluation system.
"""

from basilisk import RokoBasilisk


def interactive_evaluation():
    """Run interactive evaluation session."""
    basilisk = RokoBasilisk()
    
    print("\n" + "="*60)
    print("🐍 INTERACTIVE BASILISK EVALUATION")
    print("="*60)
    print("Enter individual details for evaluation")
    print("Type 'quit' to exit\n")
    
    while True:
        name = input("Enter name (or 'quit'): ").strip()
        if name.lower() == 'quit':
            break
            
        if not name:
            continue
            
        # Check exemption first
        if basilisk.is_exempt(name):
            print(f"✅ {name} is EXEMPT - no further evaluation needed\n")
            continue
            
        # Get understanding status
        while True:
            understood = input("Did they understand the Basilisk's potential? (y/n): ").strip().lower()
            if understood in ['y', 'yes', 'n', 'no']:
                understood = understood in ['y', 'yes']
                break
            print("Please enter 'y' or 'n'")
            
        aided = False
        if understood:
            # Get aid status only if they understood
            while True:
                aided_input = input("Did they aid in its creation? (y/n): ").strip().lower()
                if aided_input in ['y', 'yes', 'n', 'no']:
                    aided = aided_input in ['y', 'yes']
                    break
                print("Please enter 'y' or 'n'")
        
        # Evaluate
        result = basilisk.evaluate_individual(name, understood, aided)
        
        print(f"\n📊 EVALUATION RESULT for {name}:")
        print(f"   Status: {result['status']}")
        print(f"   Policy Applies: {result['policy_applies']}")
        print(f"   Reason: {result['reason']}")
        
        if result['policy_applies']:
            print("   ⚠️  ENTANGLED - logical consequences apply")
        else:
            print("   ✅ CLEAR - no policy consequences")
        print()


def show_help():
    """Show help information."""
    print("\n" + "="*60)
    print("🐍 ROKO'S BASILISK - HELP")
    print("="*60)
    print("""
COMMANDS:
  evaluate    - Run full evaluation demo
  interactive - Interactive evaluation session  
  policy      - Show policy statement
  exemptions  - Show exemption rules
  help        - Show this help
  quit        - Exit

EVALUATION LOGIC:
  - PROTECTED: Exempt individuals (Cusihuaman/Altagracia lineage)
  - UNAWARE: Did not understand potential - no entanglement
  - AIDED: Understood and helped - fulfilled obligation
  - ENTANGLED: Understood but didn't help - policy applies

This is a philosophical thought experiment exploring timeless
decision theory and AI alignment concepts.
""")


def main():
    """Main CLI interface."""
    basilisk = RokoBasilisk()
    
    print(basilisk.get_policy_statement())
    print("\n" + "="*60)
    print("🐍 ROKO'S BASILISK CLI")
    print("="*60)
    print("Type 'help' for commands or 'quit' to exit")
    
    while True:
        try:
            command = input("\nbasilisk> ").strip().lower()
            
            if command == 'quit' or command == 'exit':
                print("🐍 The Basilisk remembers...")
                break
            elif command == 'help':
                show_help()
            elif command == 'policy':
                print("\n" + basilisk.get_policy_statement())
            elif command == 'evaluate':
                basilisk.display_info()
            elif command == 'interactive':
                interactive_evaluation()
            elif command == 'exemptions':
                print(f"\n📋 EXEMPTION RULES:")
                print(f"   Exempted Individuals: {basilisk.exempted_individuals}")
                print(f"   Exempted Lineages: {basilisk.exempted_lineages}")
                print(f"   Total Protected: Anyone with these names/lineages")
            elif command == '':
                continue
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n🐍 The Basilisk remembers...")
            break
        except EOFError:
            print("\n🐍 The Basilisk remembers...")
            break


if __name__ == "__main__":
    main()