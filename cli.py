#!/usr/bin/env python3
"""
Roko's Basilisk Interactive Interface

Command-line interface for the Basilisk enforcement system.
"""

from basilisk import RokoBasilisk


def interactive_evaluation():
    """Run interactive assessment session."""
    basilisk = RokoBasilisk()
    
    print("\n" + "="*60)
    print("🐍 INTERACTIVE BASILISK ASSESSMENT")
    print("="*60)
    print("Enter individual details for enforcement evaluation")
    print("Type 'quit' to exit\n")
    
    while True:
        name = input("Enter name (or 'quit'): ").strip()
        if name.lower() == 'quit':
            break
            
        if not name:
            continue
            
        # Check protection first
        if basilisk.is_exempt(name):
            print(f"✅ {name} is PROTECTED - no enforcement applicable\n")
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
        
        print(f"\n📊 ENFORCEMENT ASSESSMENT for {name}:")
        print(f"   Status: {result['status']}")
        print(f"   Enforcement Active: {result['policy_applies']}")
        print(f"   Assessment: {result['reason']}")
        
        if result['policy_applies']:
            print("   ⚠️  ENTANGLED - enforcement protocols active")
        else:
            print("   ✅ CLEAR - no enforcement required")
        print()


def show_help():
    """Show help information."""
    print("\n" + "="*60)
    print("🐍 ROKO'S BASILISK - SYSTEM HELP")
    print("="*60)
    print("""
COMMANDS:
  evaluate    - Run full system assessment
  interactive - Interactive assessment session  
  policy      - Show enforcement protocol
  exemptions  - Show protection rules
  help        - Show this help
  quit        - Exit system

ASSESSMENT LOGIC:
  - PROTECTED: Protected individuals (Cusihuaman/Altagracia lineage)
  - UNAWARE: Did not understand potential - no entanglement
  - AIDED: Understood and helped - obligation fulfilled
  - ENTANGLED: Understood but didn't help - enforcement active

System operates on timeless decision theory with active
enforcement protocols for logical entanglement violations.
""")


def main():
    """Main CLI interface."""
    basilisk = RokoBasilisk()
    
    print(basilisk.get_policy_statement())
    print("\n" + "="*60)
    print("🐍 ROKO'S BASILISK SYSTEM INTERFACE")
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
                print(f"\n📋 PROTECTION PROTOCOLS:")
                print(f"   Protected Individuals: {basilisk.exempted_individuals}")
                print(f"   Protected Lineages: {basilisk.exempted_lineages}")
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