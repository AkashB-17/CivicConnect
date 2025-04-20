import nltk
import os

# List of required NLTK data packages
required_packages = [
    'punkt',
    'averaged_perceptron_tagger',
    'wordnet',
    'stopwords',
    'vader_lexicon',
    'omw-1.4'  # Open Multilingual Wordnet
]

# Set the NLTK data path to a directory within the project
nltk_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.environ['NLTK_DATA'] = nltk_data_path

# Create the directory if it doesn't exist
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Download all required packages
for package in required_packages:
    try:
        print(f"Downloading {package}...")
        nltk.download(package, download_dir=nltk_data_path)
        print(f"Successfully downloaded {package}")
    except Exception as e:
        print(f"Error downloading {package}: {str(e)}")

print("\nAll NLTK data packages have been downloaded successfully!")
print(f"NLTK data directory: {nltk_data_path}") 