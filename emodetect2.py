import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import warnings
from sklearn.exceptions import UndefinedMetricWarning

def create_dataset():
    data = {
        'text': [
            "I am so happy today!",
            "This is wonderful news",
            "I feel great",
            "I'm so excited about this",
            "I feel really sad",
            "This is terrible",
            "I'm so depressed",
            "Why does this always happen to me",
            "I'm so angry right now",
            "This makes me furious",
            "I hate this so much",
            "I'm really annoyed",
            "I feel neutral about this",
            "It's just okay",
            "Nothing special",
            "I don't know how I feel"
        ],
        'emotion': [
            'happy', 'happy', 'happy', 'happy',
            'sad', 'sad', 'sad', 'sad',
            'angry', 'angry', 'angry', 'angry',
            'neutral', 'neutral', 'neutral', 'neutral'
        ]
    }
    return pd.DataFrame(data)

def train_model(df):
    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['emotion'], test_size=0.2, random_state=42
    )
    
    model = make_pipeline(
        TfidfVectorizer(),
        MultinomialNB()
    )
    
    model.fit(X_train, y_train)
    
    warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

    print("Model Evaluation:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    return model

def keyword_override(user_input, emotion_keywords):
    lowered = user_input.lower()
    for emotion, keywords in emotion_keywords.items():
        for kw in keywords:
            if kw in lowered:
                return emotion
    return None

def run_cli_bot(model):
    emotion_keywords = {
        'happy': ['happy', 'great', 'excited', 'wonderful', 'joy', 'smiling'],
        'sad': ['sad', 'terrible', 'depressed', 'happen', 'cry'],
        'angry': ['angry', 'hate', 'furious', 'annoyed', 'mad'],
        'neutral': ['neutral', 'okay', 'nothing', 'fine', 'whatever']
    }
    
    responses = {
        'happy': "That's great! Keep spreading positivity!",
        'sad': "I'm sorry to hear that. Remember, tough times don't last forever.",
        'angry': "Take a deep breath. Try to stay calm - you've got this.",
        'neutral': "Sometimes it's okay to feel just okay."
    }
    
    print("\nEmotion Detection CLI Bot")
    print("Type a sentence and I'll try to detect your emotion.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ")
        except KeyboardInterrupt:
            print("\nGoodbye! Take care.")
            break

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! Take care.")
            break
            
        if not user_input.strip():
            print("Please type something meaningful.")
            continue

        emotion = keyword_override(user_input, emotion_keywords)
        if not emotion:
            emotion = model.predict([user_input])[0]

        print(f"Detected mood: {emotion}")
        print(f"Common keywords for '{emotion}': {', '.join(emotion_keywords[emotion])}")
        print(f"Bot: {responses.get(emotion, 'I\'m not sure how to respond to that.')}\n")

def main():
    print("Creating emotion dataset...")
    df = create_dataset()
    
    print("Training model...")
    model = train_model(df)
    
    run_cli_bot(model)

if __name__ == "__main__":
    main()
