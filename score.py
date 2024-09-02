import json

def read_profile_data(file_path):
    """Reads profile data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

def calculate_profile_score(profile):
    score = 0
    breakdown = []

    # Check profile photo
    if profile.get('has_profile_picture', False):
        score += 10
        breakdown.append("Profile Picture: +10 points")
    else:
        breakdown.append("No Profile Picture: -10 points")
        score -= 10

    # Check about section
    if profile.get('about', None):
        score += 10
        breakdown.append("About Section: +10 points")
    else:
        breakdown.append("No About Section: -10 points")
        score -= 10

    # Check experience section
    experience = profile.get('experience', [])
    if experience:
        score += 10
        breakdown.append("Experience Section: +10 points")
        detailed_exp = any('date_range' in exp and 'duration' in exp for exp in experience)
        if detailed_exp:
            score += 5
            breakdown.append("Detailed Experience: +5 points")
        else:
            breakdown.append("No Detailed Experience: -5 points")
            score -= 5
    else:
        breakdown.append("No Experience Listed: -10 points")
        score -= 10

    # Check activity level (connections)
    connections = profile.get('number_connections', '0').replace(',', '')
    if connections.isdigit() and int(connections) > 500:
        score += 15
        breakdown.append("Connections (Activity Level): +15 points")
    elif connections.isdigit() and int(connections) > 100:
        score += 10
        breakdown.append("Connections (Moderate Activity Level): +10 points")
    else:
        breakdown.append("Low Connections: -5 points")
        score -= 5

    # Check skills
    if len(experience) > 0 or len(profile.get('education', [])) > 0:
        score += 5
        breakdown.append("Skills: +5 points")
    else:
        breakdown.append("No Skills Detected: -5 points")
        score -= 5

    # Check education
    education = profile.get('education', [])
    if education:
        score += 5
        breakdown.append("Education: +5 points")
    else:
        breakdown.append("No Education Listed: -5 points")
        score -= 5

    # Check recommendations
    if profile.get('number_recommendations', None):
        score += 5
        breakdown.append("Recommendations: +5 points")
    else:
        breakdown.append("No Recommendations: -5 points")
        score -= 5

    # Check interests
    if profile.get('interests'):
        score += 5
        breakdown.append("Interests: +5 points")
    else:
        breakdown.append("No Interests: -5 points")
        score -= 5

    return score, breakdown

def main():
    # Path to the config.json file
    config_file_path = 'linkedin_profiles.json'

    # Read profile data from config.json
    profile_data_list = read_profile_data(config_file_path)

    if profile_data_list and isinstance(profile_data_list, list):
        # Loop through each profile and calculate the score
        for idx, profile in enumerate(profile_data_list):
            profile_score, score_breakdown = calculate_profile_score(profile)
            print(f"\nProfile {idx + 1} Score: {profile_score}/100")
            print("Score Breakdown:")
            for line in score_breakdown:
                print(f"- {line}")
    else:
        print("Failed to read profile data or the data format is incorrect.")

if __name__ == "__main__":
    main()
