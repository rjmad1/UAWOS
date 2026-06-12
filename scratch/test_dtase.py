# scratch/test_dtase.py
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uawos_dtase


def run_tests():
    print("==================================================")
    print("STARTING UAWOS DTASE VERIFICATION TESTS")
    print("==================================================")

    test_cases = [
        {
            "name": "Overtime Intimidation Narrative",
            "text": "I worked 12 hours overtime this week on the product launch, but my supervisor denied my overtime compensation claim and threatened that if I escalated it to HR, I would be terminated immediately. This is totally illegal and violating my contract.",
        },
        {
            "name": "Evening Headaches Symptom Narrative",
            "text": "I have been getting severe tension headaches every evening after finishing work. The symptoms usually start around 6 PM, causing head pain and fatigue. I am not taking any medications and need a clinical evaluation plan.",
        },
        {
            "name": "Checkout Abandonment User Feedback",
            "text": "We have a critical user experience issue in our e-commerce product. Customers are repeatedly abandoning checkout and leaving the site as soon as the shipping fees are displayed at the final step. We need user stories and a roadmap feature to solve this.",
        },
    ]

    for case in test_cases:
        print(f"\n--- Testing Scenario: {case['name']} ---")
        text = case["text"]

        # Test 1: Identify Domains (FR-252)
        print("\n1. Domain Identification (FR-252):")
        domains = uawos_dtase.identify_domains(text)
        for d in domains:
            print(f"   - Domain: {d['domain']:<20} | Confidence: {d['confidence']:.2f} | Evidence: {d['evidence']}")

        primary_domains = [d["domain"] for d in domains if d["confidence"] >= 0.4]
        if not primary_domains:
            primary_domains = [domains[0]["domain"]]

        # Test 2: Apply Translation Frameworks (FR-253)
        print("\n2. Specialized Domain Translations (FR-253):")
        translations = uawos_dtase.apply_domain_frameworks(text, primary_domains)
        for dom, trans in translations.items():
            print(f"   * Domain: {dom.upper()}")
            print(f"     Framework: {trans.get('framework')}")
            for key, val in trans.items():
                if key != "framework":
                    print(f"     {key.replace('_', ' ').capitalize()}: {str(val)[:150]}...")

        # Test 3: Discover Opportunities, Risks, Anomalies (FR-255)
        print("\n3. Opportunities, Risks & Anomalies Discovery (FR-255):")
        insights = uawos_dtase.discover_opportunities_risks_anomalies(text)
        print("   * Discovered Opportunities:")
        for opp in insights["opportunities"]:
            print(f"     - [{opp['type']}] {opp['description']} (Conf: {opp['confidence']:.2f})")
            print(f'       Quote: "{opp["evidence"]}"')

        print("   * Discovered Risks:")
        for risk in insights["risks"]:
            print(f"     - [{risk['type']}] {risk['description']} (Conf: {risk['confidence']:.2f})")
            print(f'       Quote: "{risk["evidence"]}"')

        print("   * Discovered Anomalies:")
        for anom in insights["anomalies"]:
            print(f"     - [{anom['type']}] {anom['description']} (Conf: {anom['confidence']:.2f})")
            print(f'       Quote: "{anom["evidence"]}"')

        # Test 4: Multi-Persona Output Generation (FR-257)
        print("\n4. Multi-Persona Output Synthesis (FR-257):")
        personas = uawos_dtase.generate_multi_persona_outputs(text, [d["domain"] for d in domains])
        for persona, output in personas.items():
            print(f"   * Persona: {persona}")
            first_lines = "\n".join(output.strip().split("\n")[:3])
            print(f"     {first_lines}\n     ...")

    print("\n==================================================")
    print("DTASE VERIFICATION TESTS COMPLETE")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
