#Script to convert ttl file from chronostratigraphic information to json
import json
import rdflib
import os
from rdflib import URIRef, Literal

#read ttl file
ttl_file = 'ChronostratChart2024-12.ttl'
#we will extract info from the ttl file and convert it to json
#load ttl file
g = rdflib.Graph()
g.parse(ttl_file, format='ttl')

# Query to extract the list of ages (members of ischart:Ages collection)
query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:Ages skos:member ?member .
    }
"""
results = g.query(query)

# Extract the age URIs from the results
age_uris = []
for row in results:
    age_uris.append(row.member)

# Create a list to store detailed information for each age
ages_detailed = []

# Define the namespaces we'll need to query
GTS = rdflib.Namespace("http://resource.geosciml.org/ontology/timescale/gts#")
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
TIME = rdflib.Namespace("http://www.w3.org/2006/time#")
ISCHART = rdflib.Namespace("http://resource.geosciml.org/classifier/ics/ischart/")
PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
SDO = rdflib.Namespace("https://schema.org/")
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
RANK = rdflib.Namespace("http://resource.geosciml.org/ontology/timescale/rank/")
TS = rdflib.Namespace("http://resource.geosciml.org/vocabulary/timescale/")

# Process each age URI to extract detailed information
for age_uri in age_uris:
    age_info = {}
    
    # Extract the age name from the URI
    age_name = str(age_uri).split('/')[-1]
    age_info['name'] = age_name
    
    # Get English preferred label if available
    for obj in g.objects(age_uri, SKOS.prefLabel):
        if obj.language == 'en':
            age_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(age_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        age_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    age_info['ratifiedGSSP'] = (age_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(age_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        age_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(age_uri, SKOS.definition):
        age_info['definition'] = str(obj)
        break
    
    # Get broader concept (parent)
    for obj in g.objects(age_uri, SKOS.broader):
        broader = str(obj).split('/')[-1]
        age_info['broader'] = broader
        break
    
    # Get notation (short code)
    for obj in g.objects(age_uri, SKOS.notation):
        age_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(age_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            age_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            age_info['beginning_error'] = float(error)
    
    for end_node in g.objects(age_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            age_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            age_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(age_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        age_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(age_uri, SH.order):
        age_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(age_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        age_info['color'] = color
        break
    
    # Add this age to our collection
    ages_detailed.append(age_info)

# Sort ages by order if available
ages_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Create a dictionary to access ages by name for later use
ages_by_name = {age_info['name']: age_info for age_info in ages_detailed}

# Now extract the epochs
epoch_query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:Epochs skos:member ?member .
    }
"""
epoch_results = g.query(epoch_query)

# Extract the epoch URIs from the results
epoch_uris = []
for row in epoch_results:
    epoch_uris.append(row.member)

# Create a list to store detailed information for each epoch
epochs_detailed = []

# Process each epoch URI to extract detailed information
for epoch_uri in epoch_uris:
    epoch_info = {}
    
    # Extract the epoch name from the URI
    epoch_name = str(epoch_uri).split('/')[-1]
    epoch_info['name'] = epoch_name
    
    # Get English preferred label if available
    for obj in g.objects(epoch_uri, SKOS.prefLabel):
        if obj.language == 'en':
            epoch_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(epoch_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        epoch_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    epoch_info['ratifiedGSSP'] = (epoch_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(epoch_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        epoch_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(epoch_uri, SKOS.definition):
        epoch_info['definition'] = str(obj)
        break
    
    # Get broader concept (parent)
    for obj in g.objects(epoch_uri, SKOS.broader):
        broader = str(obj).split('/')[-1]
        epoch_info['broader'] = broader
        break
    
    # Get notation (short code)
    for obj in g.objects(epoch_uri, SKOS.notation):
        epoch_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(epoch_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            epoch_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            epoch_info['beginning_error'] = float(error)
    
    for end_node in g.objects(epoch_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            epoch_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            epoch_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(epoch_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        epoch_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(epoch_uri, SH.order):
        epoch_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(epoch_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        epoch_info['color'] = color
        break
    
    # Get narrower/children concepts and add detailed child data
    narrower_concepts = []
    for obj in g.objects(epoch_uri, SKOS.narrower):
        narrower_name = str(obj).split('/')[-1]
        narrower_concepts.append(narrower_name)
    
    # Get the full detailed age data for each child
    children_data = []
    for child_name in narrower_concepts:
        if child_name in ages_by_name:
            children_data.append(ages_by_name[child_name])
    
    epoch_info['children'] = children_data
    
    # Add this epoch to our collection
    epochs_detailed.append(epoch_info)

# Sort epochs by order if available
epochs_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Create a dictionary to access epochs by name for later use
epochs_by_name = {epoch_info['name']: epoch_info for epoch_info in epochs_detailed}

# Now extract the periods
period_query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:Periods skos:member ?member .
    }
"""
period_results = g.query(period_query)

# Extract the period URIs from the results
period_uris = []
for row in period_results:
    period_uris.append(row.member)

# Create a list to store detailed information for each period
periods_detailed = []

# Process each period URI to extract detailed information
for period_uri in period_uris:
    period_info = {}
    
    # Extract the period name from the URI
    period_name = str(period_uri).split('/')[-1]
    period_info['name'] = period_name
    
    # Get English preferred label if available
    for obj in g.objects(period_uri, SKOS.prefLabel):
        if obj.language == 'en':
            period_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(period_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        period_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    period_info['ratifiedGSSP'] = (period_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(period_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        period_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(period_uri, SKOS.definition):
        period_info['definition'] = str(obj)
        break
    
    # Get broader concept (parent)
    for obj in g.objects(period_uri, SKOS.broader):
        broader = str(obj).split('/')[-1]
        period_info['broader'] = broader
        break
    
    # Get notation (short code)
    for obj in g.objects(period_uri, SKOS.notation):
        period_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(period_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            period_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            period_info['beginning_error'] = float(error)
    
    for end_node in g.objects(period_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            period_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            period_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(period_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        period_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(period_uri, SH.order):
        period_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(period_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        period_info['color'] = color
        break
    
    # Get narrower/children concepts
    narrower_concepts = []
    for obj in g.objects(period_uri, SKOS.narrower):
        narrower_name = str(obj).split('/')[-1]
        narrower_concepts.append(narrower_name)
    
    # Get the full detailed epoch data for each child
    children_data = []
    for child_name in narrower_concepts:
        if child_name in epochs_by_name:
            children_data.append(epochs_by_name[child_name])
    
    period_info['children'] = children_data
    
    # Add this period to our collection
    periods_detailed.append(period_info)

# Sort periods by order if available
periods_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Create a dictionary to access periods by name for later use
periods_by_name = {period_info['name']: period_info for period_info in periods_detailed}

# Now extract the eras
era_query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:Eras skos:member ?member .
    }
"""
era_results = g.query(era_query)

# Extract the era URIs from the results
era_uris = []
for row in era_results:
    era_uris.append(row.member)

# Create a list to store detailed information for each era
eras_detailed = []

# Process each era URI to extract detailed information
for era_uri in era_uris:
    era_info = {}
    
    # Extract the era name from the URI
    era_name = str(era_uri).split('/')[-1]
    era_info['name'] = era_name
    
    # Get English preferred label if available
    for obj in g.objects(era_uri, SKOS.prefLabel):
        if obj.language == 'en':
            era_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(era_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        era_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    era_info['ratifiedGSSP'] = (era_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(era_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        era_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(era_uri, SKOS.definition):
        era_info['definition'] = str(obj)
        break
    
    # Get broader concept (parent)
    for obj in g.objects(era_uri, SKOS.broader):
        broader = str(obj).split('/')[-1]
        era_info['broader'] = broader
        break
    
    # Get notation (short code)
    for obj in g.objects(era_uri, SKOS.notation):
        era_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(era_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            era_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            era_info['beginning_error'] = float(error)
    
    for end_node in g.objects(era_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            era_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            era_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(era_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        era_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(era_uri, SH.order):
        era_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(era_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        era_info['color'] = color
        break
    
    # Get narrower/children concepts
    narrower_concepts = []
    for obj in g.objects(era_uri, SKOS.narrower):
        narrower_name = str(obj).split('/')[-1]
        narrower_concepts.append(narrower_name)
    
    # Get the full detailed period data for each child
    children_data = []
    for child_name in narrower_concepts:
        if child_name in periods_by_name:
            children_data.append(periods_by_name[child_name])
    
    era_info['children'] = children_data
    
    # Add this era to our collection
    eras_detailed.append(era_info)

# Sort eras by order if available
eras_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Create a dictionary to access eras by name for later use
eras_by_name = {era_info['name']: era_info for era_info in eras_detailed}

# Now extract the eons
eon_query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:Eons skos:member ?member .
    }
"""
eon_results = g.query(eon_query)

# Extract the eon URIs from the results
eon_uris = []
for row in eon_results:
    eon_uris.append(row.member)

# Create a list to store detailed information for each eon
eons_detailed = []

# Process each eon URI to extract detailed information
for eon_uri in eon_uris:
    eon_info = {}
    
    # Extract the eon name from the URI
    eon_name = str(eon_uri).split('/')[-1]
    eon_info['name'] = eon_name
    
    # Get English preferred label if available
    for obj in g.objects(eon_uri, SKOS.prefLabel):
        if obj.language == 'en':
            eon_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(eon_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        eon_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    eon_info['ratifiedGSSP'] = (eon_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(eon_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        eon_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(eon_uri, SKOS.definition):
        eon_info['definition'] = str(obj)
        break
    
    # Get broader concept (parent)
    for obj in g.objects(eon_uri, SKOS.broader):
        broader = str(obj).split('/')[-1]
        eon_info['broader'] = broader
        break
    
    # Get notation (short code)
    for obj in g.objects(eon_uri, SKOS.notation):
        eon_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(eon_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            eon_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            eon_info['beginning_error'] = float(error)
    
    for end_node in g.objects(eon_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            eon_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            eon_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(eon_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        eon_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(eon_uri, SH.order):
        eon_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(eon_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        eon_info['color'] = color
        break
    
    # Get narrower/children concepts
    narrower_concepts = []
    for obj in g.objects(eon_uri, SKOS.narrower):
        narrower_name = str(obj).split('/')[-1]
        narrower_concepts.append(narrower_name)
    
    # Get the full detailed era data for each child
    children_data = []
    for child_name in narrower_concepts:
        if child_name in eras_by_name:
            children_data.append(eras_by_name[child_name])
    
    eon_info['children'] = children_data
    
    # Add this eon to our collection
    eons_detailed.append(eon_info)

# Sort eons by order if available
eons_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Create a dictionary to access eons by name for later use
eons_by_name = {eon_info['name']: eon_info for eon_info in eons_detailed}

# Finally, extract the super-eons
supereon_query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ischart: <http://resource.geosciml.org/classifier/ics/ischart/>
    
    SELECT ?member
    WHERE {
        ischart:SuperEons skos:member ?member .
    }
"""
supereon_results = g.query(supereon_query)

# Extract the super-eon URIs from the results
supereon_uris = []
for row in supereon_results:
    supereon_uris.append(row.member)

# Create a list to store detailed information for each super-eon
supereons_detailed = []

# Process each super-eon URI to extract detailed information
for supereon_uri in supereon_uris:
    supereon_info = {}
    
    # Extract the super-eon name from the URI
    supereon_name = str(supereon_uri).split('/')[-1]
    supereon_info['name'] = supereon_name
    
    # Get English preferred label if available
    for obj in g.objects(supereon_uri, SKOS.prefLabel):
        if obj.language == 'en':
            supereon_info['prefLabel'] = str(obj)
            break
    
    # Get rank
    for obj in g.objects(supereon_uri, GTS.rank):
        rank_value = str(obj).split('/')[-1]
        supereon_info['rank'] = rank_value
        break
    
    # Check if ratifiedGSSP is true
    supereon_info['ratifiedGSSP'] = (supereon_uri, GTS.ratifiedGSSP, Literal(True)) in g
    
    # Get isDefinedBy
    for obj in g.objects(supereon_uri, RDFS.isDefinedBy):
        defined_by = str(obj).split(':')[-1]
        supereon_info['isDefinedBy'] = defined_by
        break
    
    # Get definition
    for obj in g.objects(supereon_uri, SKOS.definition):
        supereon_info['definition'] = str(obj)
        break
    
    # Get notation (short code)
    for obj in g.objects(supereon_uri, SKOS.notation):
        supereon_info['notation'] = str(obj)
        break
    
    # Get time beginning and ending
    for beginning_node in g.objects(supereon_uri, TIME.hasBeginning):
        for mya in g.objects(beginning_node, ISCHART.inMYA):
            supereon_info['beginning'] = float(mya)
        for error in g.objects(beginning_node, SDO.marginOfError):
            supereon_info['beginning_error'] = float(error)
    
    for end_node in g.objects(supereon_uri, TIME.hasEnd):
        for mya in g.objects(end_node, ISCHART.inMYA):
            supereon_info['ending'] = float(mya)
        for error in g.objects(end_node, SDO.marginOfError):
            supereon_info['ending_error'] = float(error)
    
    # Get derivedFrom
    for obj in g.objects(supereon_uri, PROV.wasDerivedFrom):
        derived_from = str(obj).split(':')[-1]
        supereon_info['derivedFrom'] = derived_from
        break
    
    # Get order
    for obj in g.objects(supereon_uri, SH.order):
        supereon_info['order'] = int(obj)
        break
    
    # Get color
    for obj in g.objects(supereon_uri, SDO.color):
        color = str(obj).replace('^^http://resource.geosciml.org/classifier/ics/ischart/RGBHex', '')
        supereon_info['color'] = color
        break
    
    # Get narrower/children concepts
    narrower_concepts = []
    for obj in g.objects(supereon_uri, SKOS.narrower):
        narrower_name = str(obj).split('/')[-1]
        narrower_concepts.append(narrower_name)
    
    # Get the full detailed eon data for each child
    children_data = []
    for child_name in narrower_concepts:
        if child_name in eons_by_name:
            children_data.append(eons_by_name[child_name])
    
    supereon_info['children'] = children_data
    
    # Add this super-eon to our collection
    supereons_detailed.append(supereon_info)

# Sort super-eons by order if available
supereons_detailed.sort(key=lambda x: x.get('order', float('inf')))

# Convert all data to JSON
ages_json = json.dumps(ages_detailed, indent=2)
epochs_json = json.dumps(epochs_detailed, indent=2)
periods_json = json.dumps(periods_detailed, indent=2)
eras_json = json.dumps(eras_detailed, indent=2)
eons_json = json.dumps(eons_detailed, indent=2)
supereons_json = json.dumps(supereons_detailed, indent=2)

# Print previews
print(f"\nFound {len(ages_detailed)} ages with detailed information")
print(f"Found {len(epochs_detailed)} epochs with detailed information")
print(f"Found {len(periods_detailed)} periods with detailed information")
print(f"Found {len(eras_detailed)} eras with detailed information")
print(f"Found {len(eons_detailed)} eons with detailed information")
print(f"Found {len(supereons_detailed)} super-eons with detailed information")

# Save to JSON files
with open('ages_detailed.json', 'w') as f:
    f.write(ages_json)
print("\nSaved detailed ages information to ages_detailed.json")

with open('epochs_detailed.json', 'w') as f:
    f.write(epochs_json)
print("Saved detailed epochs information to epochs_detailed.json")

with open('periods_detailed.json', 'w') as f:
    f.write(periods_json)
print("Saved detailed periods information to periods_detailed.json")

with open('eras_detailed.json', 'w') as f:
    f.write(eras_json)
print("Saved detailed eras information to eras_detailed.json")

with open('eons_detailed.json', 'w') as f:
    f.write(eons_json)
print("Saved detailed eons information to eons_detailed.json")

with open('supereons_detailed.json', 'w') as f:
    f.write(supereons_json)
print("Saved detailed super-eons information to supereons_detailed.json")

# Create a complete hierarchical structure starting from super-eons
complete_hierarchy = supereons_detailed

# Save the complete hierarchical structure
complete_json = json.dumps(complete_hierarchy, indent=2)
with open('complete_hierarchy.json', 'w') as f:
    f.write(complete_json)
print("Saved complete hierarchical structure to complete_hierarchy.json")

