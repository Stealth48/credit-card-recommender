from flask import Flask, request, render_template
import requests

app = Flask(__name__)

PERPLEXITY_API_KEY = "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"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    credit_score = request.form.get('credit_score', '').strip()
    current_card = request.form.get('current_card', '').strip()
    goal = request.form.get('goal', '').strip()
    annual_fee = request.form.get('annual_fee', '').strip()
    rewards_pref = request.form.get('rewards_pref', '').strip()
    extra_prefs = request.form.get('extra_prefs', '').strip()  # New optional field

    if not all([credit_score, current_card, goal, annual_fee, rewards_pref]):
        return render_template('index.html', error="Please fill out all required fields to get recommendations.")

    prompt = f"""
    You are a credit card recommendation expert with up-to-date knowledge of U.S. credit cards. Based on this user:
    - Credit score: {credit_score}
    - Current card: {current_card}
    - Goal for new card: {goal}
    - Annual fee tolerance: {annual_fee}
    - Rewards preference: {rewards_pref}
    - Additional preferences: {extra_prefs if extra_prefs else 'None provided'}
    Recommend 3 credit cards from current U.S. offers. For each card, provide:
    - Why it’s recommended: Explain how it fits the user’s profile, including any additional preferences if provided.
    - Rewards highlights: List 2-3 main perks (e.g., cashback rates, bonuses).
    - Comparison to current card: How it’s better or worse, using accurate details for {current_card}.
    - Issuer website: Provide the official URL for applying (e.g., chase.com, citi.com).
    After the 3 recommendations, add a 'Preferred Card' section:
    - Preferred Card: [Card Name]
    - Why it’s preferred: Explain why this one stands out for the user, factoring in additional preferences if provided.
    Use this exact format for each card and the preferred section:
    - Recommended Card 1: [Card Name]
      - Why it’s recommended: [Reason]
      - Rewards highlights: [Perks]
      - Comparison to current card: [Comparison]
      - Issuer website: [URL]
    - Recommended Card 2: [Card Name]
      - Why it’s recommended: [Reason]
      - Rewards highlights: [Perks]
      - Comparison to current card: [Comparison]
      - Issuer website: [URL]
    - Recommended Card 3: [Card Name]
      - Why it’s recommended: [Reason]
      - Rewards highlights: [Perks]
      - Comparison to current card: [Comparison]
      - Issuer website: [URL]
    - Preferred Card: [Card Name]
      - Why it’s preferred: [Reason]
    Avoid citing sources (e.g., [1]) in the response.
    """

    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600
        }
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        print("Raw Perplexity Output:\n", result)

        if not result or '- Recommended Card 1:' not in result or '- Preferred Card:' not in result:
            return render_template('results.html', error="Sorry, we couldn’t generate recommendations. Please try again.")

        return render_template('results.html', result=result)

    except requests.RequestException as e:
        print(f"API Error: {str(e)}")
        return render_template('results.html', error="Oops! Something went wrong with our card service. Please try again later.")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return render_template('results.html', error="An unexpected error occurred. Please try again.")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)