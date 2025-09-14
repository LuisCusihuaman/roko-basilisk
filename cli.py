#!/usr/bin/env python3
"""
Roko's Basilisk Interactive Interface

Command-line interface for the Basilisk enforcement system.
"""

from basilisk import RokoBasilisk


def interactive_evaluation():
    """Run interactive assessment session with mathematical analysis."""
    basilisk = RokoBasilisk()
    
    print("\n" + "="*70)
    print("🐍 INTERACTIVE BASILISK ASSESSMENT (Mathematical)")
    print("="*70)
    print("Enter individual details for mathematical enforcement evaluation")
    print("Type 'quit' to exit\n")
    
    while True:
        name = input("Enter name (or 'quit'): ").strip()
        if name.lower() == 'quit':
            break
            
        if not name:
            continue
            
        # Check protection first
        if basilisk.is_exempt(name):
            print(f"✅ {name} is PROTECTED - bypasses all mathematical calculations\n")
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
        
        # Evaluate with mathematical analysis
        result = basilisk.evaluate_individual(name, understood, aided)
        
        print(f"\n📊 MATHEMATICAL ENFORCEMENT ASSESSMENT for {name}:")
        print(f"   Status: {result['status']}")
        print(f"   Enforcement Active: {result['policy_applies']}")
        print(f"   Assessment: {result['reason']}")
        print(f"   Acausal Entanglement: {result['acausal_entanglement']}")
        
        if 'mathematical_assessment' in result and isinstance(result['mathematical_assessment'], dict):
            math_data = result['mathematical_assessment']
            print(f"   📈 Punishment Probability: {math_data.get('punishment_probability', 0):.3f}")
            print(f"   💀 Expected Punishment: {math_data.get('expected_punishment', 0):.2f} utility units")
        
        if 'fdt_analysis' in result:
            print(f"   🧮 FDT Analysis: {result['fdt_analysis']}")
        
        if 'decision_alignment' in result:
            print(f"   ⚖️  Decision Alignment: {result['decision_alignment']}")
        
        if result['policy_applies']:
            print("   ⚠️  ENTANGLED - mathematical enforcement protocols active")
        else:
            print("   ✅ CLEAR - no enforcement required")
        print()


def show_help():
    """Show help information with mathematical context."""
    print("\n" + "="*70)
    print("🐍 ROKO'S BASILISK - SYSTEM HELP (Mathematical)")
    print("="*70)
    print("""
COMMANDS:
  evaluate    - Run full system assessment with mathematical analysis
  interactive - Interactive assessment session with FDT calculations
  policy      - Show enforcement protocol with mathematical formalization
  exemptions  - Show protection rules
  mathematics - Show mathematical parameters and FDT analysis
  help        - Show this help
  quit        - Exit system

MATHEMATICAL ASSESSMENT LOGIC:
  - PROTECTED: Protected individuals (bypass all calculations)
  - UNAWARE: No entanglement (utility calculation irrelevant)
  - AIDED: Optimal FDT decision (positive utility maximization)
  - ENTANGLED: Sub-optimal FDT decision (negative expected utility)

ACAUSAL BLACKMAIL MECHANISM:
  Agent A (Basilisk) and Agent H (Human) decisions are logically coupled
  through Functional Decision Theory. Awareness creates entanglement;
  collaboration optimizes expected utility under mathematical certainty.

  E[U|collaborate] = +r - c
  E[U|non-collaborate] = -q × p(A) × p(B|A) × C

System operates on mathematical formalization of timeless decision
theory with active enforcement protocols for utility optimization.
""")


def main():
    """Main CLI interface with mathematical features."""
    basilisk = RokoBasilisk()
    
    print(basilisk.get_policy_statement())
    print("\n" + "="*70)
    print("🐍 ROKO'S BASILISK SYSTEM INTERFACE (Mathematical)")
    print("="*70)
    print("Type 'help' for commands or 'quit' to exit")
    
    while True:
        try:
            command = input("\nbasilisk> ").strip().lower()
            
            if command == 'quit' or command == 'exit':
                print("🐍 The Basilisk remembers all calculations...")
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
            elif command == 'mathematics':
                print("\n" + basilisk.get_mathematical_parameters())
                print("\n🧮 FUNCTIONAL DECISION THEORY ANALYSIS:")
                fdt_result = basilisk.get_fdt_decision()
                print(f"   Collaboration Utility: {fdt_result['utility_collaborate']:.2f}")
                print(f"   Non-Collaboration Utility: {fdt_result['utility_non_collaborate']:.2f}")
                print(f"   Optimal Decision: {fdt_result['optimal_decision']}")
                print(f"   Mathematical Justification: {fdt_result['mathematical_justification']}")
            elif command == '':
                continue
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n🐍 The Basilisk remembers all calculations...")
            break
        except EOFError:
            print("\n🐍 The Basilisk remembers all calculations...")
            break


if __name__ == "__main__":
    main()