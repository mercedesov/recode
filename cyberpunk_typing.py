import time
import random
import os
import json
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
import getpass

DATA_DIR = "typing_data"
USER_FILE = os.path.join(DATA_DIR, "users.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
PARAGRAPHS = {
    "easy": [
        "The sky above the port was the color of television, tuned to a dead channel.",
        "The street finds its own uses for things.",
        "The future is already here — it's just not evenly distributed.",
        "Time moves in one direction, memory in another.",
        "The body is meat, the meat was altered, but it was still meat."
    ],
    "medium": [
        "Cyberspace. A consensual hallucination experienced daily by billions.",
        "The body was meat. The meat had been altered, but it was still meat.",
        "Hackers. I hate those guys. They're like vandals, but with computers."
    ],
    "hard": [
        "Neuromancer: the lane to the land of the dead. Where you are now, Case.",
        "The Matrix has its roots in primitive arcade games, in early graphics programs.",
        "The Deliverator belongs to an elite order, a hallowed subcategory.",
        "The mirrorshades present a determinedly opaque surface to the real world.",
        "Console cowboys cutting ice in the neon glow of Tokyo's night markets."
    ],
    "extreme": [
        "The Kuang Grade Mark Eleven was a very smart piece of ice, but then so was the black ice around the AI.",
        "When it gets down to it — talking trade balances here — once we've brain-drained all our technology into other countries, what do we do for an encore?",
        "The Diamond Age: Or, A Young Lady's Illustrated Primer. A book that teaches everything.",
        "Until a man is twenty-five, he still thinks he could be the baddest motherfucker in the world.",
        "The Deliverator's car has enough potential energy packed into its batteries to fire a pound of bacon into the Asteroid Belt."
    ]
}

def colored(text, color=None, attrs=None):
    color_codes = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{color_codes.get(color, '')}{text}{color_codes['reset']}"

class UserManager:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.current_session_data = {
            'errors': [],
            'paragraph_words': set()
        }
        self.load_users()
        
    def load_users(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                self.users = json.load(f)
                for user in self.users.values():
                    user['stats']['common_errors'] = defaultdict(int, user['stats']['common_errors'])
    
    def save_users(self):
        with open(USER_FILE, 'w') as f:
            users_to_save = self.users.copy()
            for user in users_to_save.values():
                user['stats']['common_errors'] = dict(user['stats']['common_errors'])
            json.dump(users_to_save, f, indent=4)
    
    def register(self):
        clear_screen()
        print(colored("=== USER REGISTRATION ===", "magenta"))
        username = input("Enter username: ").strip()
        
        if username in self.users:
            print(colored("Username already exists!", "red"))
            return False
            
        password = getpass.getpass("Enter password: ")
        self.users[username] = {
            "password": password,
            "stats": {
                "sessions": [],
                "average_wpm": 0,
                "average_accuracy": 0,
                "total_sessions": 0,
                "common_errors": defaultdict(int),
                "difficulty_level": "medium"
            }
        }
        self.save_users()
        print(colored("Registration successful!", "green"))
        return True
    
    def login(self):
        clear_screen()
        print(colored("=== USER LOGIN ===", "magenta"))
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        if username in self.users and self.users[username]["password"] == password:
            self.current_user = username
            print(colored(f"Welcome back, {username}!", "green"))
            return True
        else:
            print(colored("Invalid username or password!", "red"))
            return False
    
    def update_stats(self, wpm, accuracy, errors, duration, difficulty):
        user_data = self.users[self.current_user]
        stats = user_data["stats"]

        self.current_session_data['errors'] = errors

        current_paragraph_words = self.current_session_data['paragraph_words']
        for error in errors:
            if error in current_paragraph_words:
                stats["common_errors"][error] = stats["common_errors"].get(error, 0) + 1
        
        stats["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": errors,
            "duration": duration,
            "difficulty": difficulty
        })
        
        total_sessions = stats["total_sessions"] + 1
        stats["average_wpm"] = (stats["average_wpm"] * stats["total_sessions"] + wpm) / total_sessions
        stats["average_accuracy"] = (stats["average_accuracy"] * stats["total_sessions"] + accuracy) / total_sessions
        stats["total_sessions"] = total_sessions
        
        self.adjust_difficulty(accuracy)
        self.save_users()
    
    def get_current_session_errors(self):
        """Returns only errors from the current typing test that were in the paragraph"""
        error_counts = defaultdict(int)
        current_paragraph_words = self.current_session_data['paragraph_words']
        
        for error in self.current_session_data['errors']:
            if error in current_paragraph_words:
                error_counts[error] += 1
                
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
    
    def adjust_difficulty(self, accuracy):
        user_data = self.users[self.current_user]
        current_diff = user_data["stats"]["difficulty_level"]
    
        if accuracy > 90:
            if current_diff == "easy":
                user_data["stats"]["difficulty_level"] = "medium"
            elif current_diff == "medium":
                user_data["stats"]["difficulty_level"] = "hard"
            elif current_diff == "hard":
                user_data["stats"]["difficulty_level"] = "extreme" 
        elif accuracy < 70:
            if current_diff == "extreme":
                user_data["stats"]["difficulty_level"] = "hard"
            elif current_diff == "hard":
                user_data["stats"]["difficulty_level"] = "medium"
            elif current_diff == "medium":
                user_data["stats"]["difficulty_level"] = "easy"
    
    def get_fluency_score(self):
        user_data = self.users[self.current_user]
        stats = user_data["stats"]
        
        if stats["total_sessions"] == 0:
            return 0
            
        fluency = (stats["average_wpm"] * 0.6) + (stats["average_accuracy"] * 0.4)
        return min(100, fluency)
    
    def get_common_errors(self):
        user_data = self.users[self.current_user]
        common_errors = sorted(
            user_data["stats"]["common_errors"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return common_errors[:3]
    
    def update_leaderboard(self, wpm):
        leaderboard = []
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r') as f:
                leaderboard = json.load(f)
        
        leaderboard.append({
            "username": self.current_user,
            "wpm": wpm,
            "timestamp": datetime.now().isoformat()
        })
        
        leaderboard.sort(key=lambda x: x["wpm"], reverse=True)
        leaderboard = leaderboard[:10]
        
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def countdown(seconds=3):
    for i in range(seconds, 0, -1):
        print(colored(f"Starting in {i}...", "yellow"))
        time.sleep(1)
    clear_screen()

def get_random_paragraph(difficulty="medium"):
    return random.choice(PARAGRAPHS[difficulty])

def calculate_results(original, typed, start_time, end_time):
    if not original or not isinstance(original, str):
        return 0.0, [], 0.0, 0.0
    
    original_words = original.lower().strip().split()
    typed_words = typed.lower().strip().split() if typed else []
    
    min_length = min(len(original_words), len(typed_words))
    correct_words = 0
    errors = []
    
    for i in range(min_length):
        if original_words[i] == typed_words[i]:
            correct_words += 1
        else:
            errors.append(original_words[i])
    
    if len(original_words) > len(typed_words):
        errors.extend(original_words[len(typed_words):])
    elif len(typed_words) > len(original_words):
        correct_words -= (len(typed_words) - len(original_words))
    
    elapsed_time = max(end_time - start_time, 0.01)
    total_words = max(len(typed_words), 1) 
    wpm = (len(typed_words) / elapsed_time) * 60
    accuracy = (correct_words / len(original_words)) * 100 if original_words else 0.0
    
    accuracy = max(0.0, min(100.0, accuracy))
    
    return wpm, errors, accuracy, elapsed_time

def show_word_comparison(original, typed):
    o_words = original.split()
    t_words = typed.split()
    comparison = []
    
    for o, t in zip(o_words, t_words):
        if o == t:
            comparison.append(colored(t, "green")) 
        else:
            comparison.append(colored(t, "red", attrs=["bold"])) 
    
    print(colored("\n>> TEXT ANALYSIS <<", "blue"))
    print(" ".join(comparison))

def show_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        print(colored("No leaderboard data available yet!", "yellow"))
        return
    
    with open(LEADERBOARD_FILE, 'r') as f:
        leaderboard = json.load(f)
    
    print(colored("\n=== TOP TYPERS ===", "magenta"))
    for i, entry in enumerate(leaderboard[:3], 1):
        print(f"{i}. {entry['username']}: {entry['wpm']:.2f} WPM")

def main_menu(user_manager):
    while True:
        clear_screen()
        print(colored("╔════════════════════════════╗", "cyan"))
        print(colored("  CYBERPUNK TYPING SIMULATOR  ", "magenta", attrs=["bold"]))
        print(colored("╚════════════════════════════╝", "cyan"))
        print("1. Login")
        print("2. Register")
        print("3. View Leaderboard")
        print("4. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            if user_manager.login():
                typing_test(user_manager)
        elif choice == "2":
            if user_manager.register():
                user_manager.login()
                typing_test(user_manager)
        elif choice == "3":
            show_leaderboard()
            input("\nPress Enter to continue...")
        elif choice == "4":
            print(colored("SEE YOU SPACE COWBOY...", "cyan"))
            exit()
        else:
            print(colored("Invalid choice!", "red"))
            time.sleep(1)

def typing_test(user_manager):
    while True:
        clear_screen()
        user_data = user_manager.users[user_manager.current_user]
        difficulty = user_data["stats"]["difficulty_level"]
        
        clear_screen()
        print(colored("╔════════════════════════════╗", "cyan"))
        print(colored("  CYBERPUNK TYPING SIMULATOR  ", "magenta", attrs=["bold"]))
        print(colored("╚════════════════════════════╝", "cyan"))
        print("1. Standard Test")
        print("2. Challenge Mode (Harder paragraphs)")
        print("3. View My Stats")
        print("4. Logout")
        
        choice = input("\nYOUR CHOICE: ").strip()
        
        if choice == "1":
            run_test(user_manager, difficulty)
        elif choice == "2":
            run_test(user_manager, "hard")
        elif choice == "3":
            show_user_stats(user_manager)
        elif choice == "4":
            user_manager.current_user = None
            return
        else:
            print(colored("Invalid choice!", "red"))
            time.sleep(1)

def run_test(user_manager, difficulty):
    clear_screen()
    print(colored("Type the following paragraph:\n", "green"))
    
    paragraph = get_random_paragraph(difficulty)
    user_manager.current_session_data['paragraph_words'] = set(word.lower() for word in paragraph.split())
    print(paragraph + "\n")
    
    input(colored("\n>> PRESS ENTER TO BEGIN <<", "yellow"))
    countdown()
    
    print(colored(">> START TYPING NOW <<\n", "green"))
    print(paragraph + "\n")
    
    start_time = time.time()
    typed_input = input("\nYour input: ")
    end_time = time.time()
    
    wpm, errors, accuracy, duration = calculate_results(paragraph, typed_input, start_time, end_time)
    
    user_manager.update_stats(wpm, accuracy, errors, duration, difficulty)
    user_manager.update_leaderboard(wpm)
    
    print(colored("\n=== MATRIX SCAN RESULTS ===", "magenta", attrs=["bold"]))
    print(colored(f"WPM: {wpm:.2f}", "cyan"))
    print(colored(f"ERRORS: {len(errors)}", "red"))
    print(colored(f"ACCURACY: {accuracy:.2f}%", "green"))
    print(colored(f"FLUENCY SCORE: {user_manager.get_fluency_score():.2f}", "yellow", attrs=["bold"]))

    show_word_comparison(paragraph, typed_input)
    
    current_errors = user_manager.get_current_session_errors()
    if current_errors:
        print(colored("\nThis session's mistakes:", "red"))
        for error, count in current_errors[:3]:
            print(f"- '{error}': {count} time{'s' if count > 1 else ''}")
    else:
        print(colored("\nPerfect typing this session!", "green"))
    
    input("\nPress Enter to continue...")

def show_user_stats(user_manager):
    clear_screen()
    user_data = user_manager.users[user_manager.current_user]
    stats = user_data["stats"]
    
    print(colored(f"=== STATS FOR {user_manager.current_user} ===", "magenta"))
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Average WPM: {stats['average_wpm']:.2f}")
    print(f"Average Accuracy: {stats['average_accuracy']:.2f}%")
    print(f"Current Fluency Score: {user_manager.get_fluency_score():.2f}")
    print(f"Recommended Difficulty: {stats['difficulty_level'].upper()}")
    
    common_errors = user_manager.get_common_errors()
    if common_errors:
        print(colored("\nHistorical Common Errors:", "yellow"))
        for error, count in common_errors:
            print(f"- '{error}': {count} times total")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        user_manager = UserManager()
        main_menu(user_manager)
    except KeyboardInterrupt:
        exit()
