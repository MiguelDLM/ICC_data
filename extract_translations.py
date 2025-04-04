import rdflib
import json
import os
from collections import defaultdict

# Define the namespaces we'll need to query
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
ISCHART = rdflib.Namespace("http://resource.geosciml.org/classifier/ics/ischart/")

def extract_translations():
    # Read and parse the TTL file
    ttl_file = 'ChronostratChart2024-12.ttl'
    g = rdflib.Graph()
    g.parse(ttl_file, format='ttl')
    
    print(f"Loaded {len(g)} triples from {ttl_file}")
    
    # Dictionary to store translations by language
    translations_by_language = defaultdict(dict)
    
    # Find all geological time periods (any subject with a prefLabel and/or altLabel)
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT DISTINCT ?subject
        WHERE {
            ?subject a skos:Concept .
            {?subject skos:prefLabel ?label} UNION {?subject skos:altLabel ?label}
        }
    """
    
    subjects = list(g.query(query))
    print(f"Found {len(subjects)} geological time periods")
    
    # Process each time period
    count = 0
    for subject in subjects:
        subject_uri = subject[0]
        
        # Get the name/identifier of this time period (last part of the URI)
        name = str(subject_uri).split('/')[-1]
        
        # Get the English label (prefLabel with @en language tag)
        english_label = None
        for obj in g.objects(subject_uri, SKOS.prefLabel):
            if getattr(obj, 'language', '') == 'en':
                english_label = str(obj)
                break
        
        # Skip if no English label found
        if not english_label:
            continue
            
        count += 1
        
        # Get translations (altLabel with various language tags)
        for obj in g.objects(subject_uri, SKOS.altLabel):
            lang = getattr(obj, 'language', '')
            if lang and lang != 'en':  # Skip if no language tag or if it's English
                translations_by_language[lang][english_label] = str(obj)
        
        # Also add the English label to the English translations
        translations_by_language['en'][english_label] = english_label
    
    print(f"Processed {count} time periods with English labels")
    
    # Create a directory for translations if it doesn't exist
    translations_dir = 'translations'
    if not os.path.exists(translations_dir):
        os.makedirs(translations_dir)
    
    # Save translations to JSON files, one for each language
    for lang, translations in translations_by_language.items():
        output_file = os.path.join(translations_dir, f"{lang}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        print(f"Created translation file for {lang} language with {len(translations)} entries: {output_file}")

if __name__ == "__main__":
    extract_translations()
    print("\nTranslation extraction completed!")
