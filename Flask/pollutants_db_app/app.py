from flask import Flask, redirect, render_template, request, send_file, send_from_directory, make_response
import io
import os, shutil
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql
from rdkit import Chem
from rdkit.Chem import Draw
from pypdb import *
import itertools
import re
import ast
from gensim.models import Word2Vec


# create an instance of Flask class
app = Flask(__name__)


# load dotenv file
load_dotenv(os.getcwd() + '/.env')


# database connection
def get_db_connection():
  # define connection parameters dictionary
  conn_params_dic = {'host' : os.getenv('POSTGRES_HOST'), 'database' : os.getenv('POSTGRES_DB'), 
                    'user' : os.getenv('POSTGRES_USER'), 'password' : os.getenv('POSTGRES_PASSWORD')}
  # create connection 
  conn = None
  print('Connecting to the PostgreSQL...........')
  conn = psycopg2.connect(**conn_params_dic)
  print('Connection successfully................')
  # return connection 
  return conn


# redirect url 
@app.route("/") 

def index():
  return redirect("/apdb/home", code=302)
  # return redirect("http://apdb.di.univr.it/apdb/home", code=302)


# define home 
@app.route("/apdb/home", methods=['GET'])

def browse():

  # run molecules
  if request.form.get('molecule_button') == 'Run':
    return render_template("molecule_table.html")

  # run bioassays
  elif request.form.get('bioassay_button') == 'Run':
    return render_template("bioassay_table.html")

  # run descriptors
  elif request.form.get('descriptor_button' == 'Run'):
    return render_template("descriptors_overview.html")

  # run similarities
  elif request.form.get('similarity_button') == 'Run':
    return render_template("similarity_panel.html")

  else:
    return render_template("browse.html")



# browse molecules 
@app.route("/apdb/home/browse-molecules", methods=['GET', 'POST'])

def molecule_browse():

  # get action
  if request.method == 'GET':

    # set id options and placeholder
    id_options = ["chemical name", "CID", "CAS", "canonical SMILES", "InchIKey", "molecular formula"]
    placeholder = "Choose an input option"
    molecule_ids = []

    # open connection
    conn = get_db_connection()
    cur = conn.cursor()
    # query all  molecules
    cur.execute('SELECT * FROM molecule_information;')
    molecules = cur.fetchall()

    # remove single quotes from chemical name
    for idx in range(len(molecules)):
      molecules[idx] = list(molecules[idx])
      molecules[idx][0] = molecules[idx][0].strip("'")
      # substitute None or NULL with 'n/a' 
      molecules[idx] = ['n/a' if (v == 'NULL' or v is None) else v for v in molecules[idx]]

    # get selected molecule id from URL
    selected_id = request.args.get('id_option', type = str)

    # check if null 
    if (selected_id == None):
      selected_placeholder = ""
    else:
      # define placeholder 
      selected_placeholder = "Type a " + selected_id + " to show a list of options"

      # convert to column names
      molecule_attribute = selected_id.strip().lower().replace(" ", "_")

      # query db for all ids 
      query = sql.SQL("SELECT {} FROM molecule_information;")
      cur.execute(query.format(sql.Identifier(molecule_attribute)))
      records = cur.fetchall()

      # iterate over tuples
      for row in records:
        # check duplicates
        if row[0] not in molecule_ids:
          molecule_ids.append(row[0])

      # remove single quotes from chemical names 
      if (not(isinstance(molecule_ids[0], int))):
        molecule_ids = [x.strip("'") for x in molecule_ids]

    # close connection 
    cur.close()
    conn.close()

    return render_template('molecule_table.html', id_options=id_options, placeholder=placeholder, molecules=molecules, 
                        selected_placeholder=selected_placeholder, molecule_ids=molecule_ids)
  
  # get action
  elif request.method == 'POST':

    # set id options and placeholder
    id_options = ["chemical name", "CID", "CAS", "canonical SMILES", "InchIKey", "molecular formula"]
    placeholder = "Choose an input option"
    filtered_molecules = []
 
    # open connection
    conn = get_db_connection()
    cur = conn.cursor()

    # get selected molecule id from URL
    selected_id = request.args.get('id_option', type = str)

     # check if null 
    if (selected_id == None):
      selected_placeholder = ""
    else: 
      # set placeholder
      selected_placeholder = "Type a " + selected_id + " to show a list of options"

      # convert to column names
      molecule_attribute = selected_id.strip().lower().replace(" ", "_")

      # get selected molecules 
      selected_molecules = request.form.get('mol_id_selection')

      # add single quotes to chemical names for query 
      if (molecule_attribute == "chemical_name"):    
        selected_molecules = "'{}'".format(selected_molecules)

      # query db for selected ids 
      try: 
        query = sql.SQL("SELECT * FROM molecule_information WHERE {pkey} = %s;").format(pkey=sql.Identifier(molecule_attribute))
        # execute query 
        cur.execute(query, (selected_molecules, ))
        filtered_molecules = cur.fetchall()
        # remove single quotes from chemical names 
        for idx in range(len(filtered_molecules)):
          filtered_molecules[idx] = list(filtered_molecules[idx])
          filtered_molecules[idx][0] = filtered_molecules[idx][0].strip("'")
          # substitute None or NULL with 'n/a' 
          filtered_molecules[idx] = ['n/a' if (v == 'NULL' or v is None) else v for v in filtered_molecules[idx]]
      except Exception:
        filtered_molecules = [] 
        
    # close connection 
    cur.close()
    conn.close()

    return render_template('molecule_table.html', id_options=id_options, placeholder=placeholder, 
                          selected_placeholder=selected_placeholder, molecules=filtered_molecules)



# filter periodic table
@app.route('/apdb/home/browse-molecules/filter', methods=['GET', 'POST'])

def molecules_filter():

  # get action
  if request.method == 'GET':

    # set id options and placeholder
    id_options = ["chemical name", "CID", "CAS", "canonical SMILES", "InchIKey", "molecular formula"]
    placeholder = "Choose an input option"
    filtered_molecules = [] 

    # open connection
    conn = get_db_connection()
    cur = conn.cursor()

    # get element to filter from URL
    element = request.args.get('element', type = str)

    # execute query 
    cur.execute('SELECT * FROM molecule_information WHERE atoms LIKE %s;', ("%{}%".format(element),))
    molecules = cur.fetchall()
    
    for row in molecules:
      # convert atoms string into list 
      atoms_list = re.sub(r"[\[\]]", "", row[6]).replace(' ', '').split(",")
      # check if selected element exists 
      if element in atoms_list:
        filtered_molecules.append(row) 

    # remove single quotes from chemical names 
    for idx in range(len(filtered_molecules)):
      filtered_molecules[idx] = list(filtered_molecules[idx])
      filtered_molecules[idx][0] = filtered_molecules[idx][0].strip("'")
      # substitute None or NULL with 'n/a' 
      filtered_molecules[idx] = ['n/a' if (v == 'NULL' or v is None) else v for v in filtered_molecules[idx]]

  return render_template('molecule_table.html', id_options=id_options, placeholder=placeholder, molecules=filtered_molecules)



# download molecule table 
@app.route('/apdb/home/browse-molecules/download', methods=['POST'])  

def molecule_download():

  # get action
  if request.method == 'POST':

    # get selected columns converting string into list
    selected_columns = ast.literal_eval(request.form.get('header'))
    # get selected molecules to download 
    molecules = ast.literal_eval(request.form.get('molecule_download'))

    # subset selected columns
    selected_molecules = []
    for row in molecules:
      selected_molecules.append([row[i] for i in selected_columns[1]])
   
    # create output df
    molecules_df = pd.DataFrame(selected_molecules, columns=selected_columns[0])
  
  # return file
  return send_file(
    io.BytesIO(molecules_df.to_csv(index=False, sep=";", encoding='utf-8').encode()),
    as_attachment=True,
    download_name='MoleculesTable.csv',
    mimetype='text/csv')



# browse bioassays
@app.route("/apdb/home/browse-bioassays", methods=['GET', 'POST'])    

def bioassay_browse():    

  # get action
  if request.method == 'GET':

    # set id options and placeholder
    id_options = ["target GI", "target geneID", "target symbol", "uniprotkb"]
    placeholder = "Choose an input option"
    target_ids = []

    # open connection
    conn = get_db_connection()
    cur = conn.cursor()
    # execute query 
    cur.execute("SELECT * FROM bioassay_data;")
    bioassays = cur.fetchall()

    # remove None target GI corresponding to duplicated tuples 
    bioassays = [i for i in bioassays if i[5] != None]

    # remove single quotes from assays names 
    for idx in range(len(bioassays)):
      bioassays[idx] = list(bioassays[idx])
      bioassays[idx][11] = bioassays[idx][11].strip("'")
      # substitute None or NULL with 'n/a' 
      bioassays[idx] = ['n/a' if (v == 'NULL' or v is None) else v for v in bioassays[idx]]

    # get selected target id from URL
    selected_id = request.args.get('id_option', type = str)
    
    # check if null
    if (selected_id == None):
      selected_placeholder = ""
    else:
      # define the placeholder 
      selected_placeholder = "Type a " + selected_id + " to show a list of options"

      # convert to column names
      target_attribute = selected_id.strip().lower().replace(" ", "_")

      # query db for all target ids 
      query = sql.SQL("SELECT {} FROM target_data;")
      # execute query 
      cur.execute(query.format(sql.Identifier(target_attribute)))
      records = cur.fetchall()

      # iterate over tuples
      for row in records:
        # remove duplicates and null values in ids list
        if (row[0] not in target_ids and not (row[0] == 'NULL' or row[0] is None)):
          target_ids.append(row[0])

    # close connection 
    cur.close()
    conn.close()

    return render_template('bioassay_table.html', id_options=id_options, placeholder=placeholder, bioassays=bioassays, 
                        selected_placeholder=selected_placeholder, target_ids=target_ids)

  # get action
  elif request.method == 'POST':

    # set id options and placeholder
    id_options = ["target GI", "target geneID", "target symbol", "uniprotkb"]
    placeholder = "Choose an input option"
    filtered_bioassays = []

    # open connection
    conn = get_db_connection()
    cur = conn.cursor()

    # get selected molecule id from URL
    selected_id = request.args.get('id_option', type = str)

    if (selected_id == None):
      selected_placeholder = ""
    else: 
      # set placeholder
      selected_placeholder = "Type a " + selected_id + " to show a list of options"

      # convert to column names
      target_attribute = selected_id.strip().lower().replace(" ", "_")

      # get selected targets 
      selected_targets = request.form.get('bio_id_selection')

      # query db for selected ids 
      try:
        query = sql.SQL("SELECT * FROM bioassay_data WHERE {pkey} = %s;").format(pkey=sql.Identifier(target_attribute))   
        # execute query 
        cur.execute(query, (selected_targets, ))
        filtered_bioassays = cur.fetchall()
        # remove single quotes from assays names 
        for idx in range(len(filtered_bioassays)):
          filtered_bioassays[idx] = list(filtered_bioassays[idx])
          filtered_bioassays[idx][11] = filtered_bioassays[idx][11].strip("'")
          # substitute None or NULL with 'n/a' 
          filtered_bioassays[idx] = ['n/a' if (v == 'NULL' or v is None) else v for v in filtered_bioassays[idx]]
      except Exception: 
        filtered_bioassays = []
        
    # close connection 
    cur.close()
    conn.close()

    return render_template('bioassay_table.html', id_options=id_options, placeholder=placeholder,
                          selected_placeholder=selected_placeholder, bioassays=filtered_bioassays)



# download bioassay table
@app.route('/apdb/home/browse-bioassays/download', methods=['GET', 'POST'])

def bioassay_download():

  # get action
  if request.method == 'POST':

    # get selected columns converting string into list
    selected_columns = ast.literal_eval(request.form.get('header'))
    # get selected bioassays to download 
    bioassays = ast.literal_eval(request.form.get('bioassay_download'))

    # subset selected columns
    selected_bioassays = []
    for row in bioassays:
      selected_bioassays.append([row[i] for i in selected_columns[1]])
   
    # create output df
    bioassays_df = pd.DataFrame(selected_bioassays[1:], columns=selected_columns[0])
  
  # return file
  return send_file(
    io.BytesIO(bioassays_df.to_csv(index=False, sep=";", encoding='utf-8').encode()),
    as_attachment=True,
    download_name='BioassaysTable.csv',
    mimetype='text/csv')


# browse targets
@app.route("/apdb/home/browse-targets", methods=['GET', 'POST'])  

def target_browse():    

    # get action
    if request.method == 'GET':

      # take uniprotkb of the selected target
      target_uniprotkb = request.args.get('target_uniprotkb', type = str)

      # open connection
      conn = get_db_connection()
      cur = conn.cursor()
      # execute query
      cur.execute('SELECT * FROM target_data WHERE uniprotkb = %s;', (target_uniprotkb, ))
      targets = cur.fetchall()
      
      # return associated molecules 
      molecules = cur.execute('SELECT cid, chemical_name, molecular_formula, canonical_smiles FROM molecule_information WHERE cid = ANY(%s);', 
                            (sorted(list(set(i[2] for i in targets))), ))
      molecules = cur.fetchall()
      # remove single quotes from chemical names 
      for idx in range(len(molecules)):
        molecules[idx] = list(molecules[idx])
        molecules[idx][1] = molecules[idx][1].strip("'")    

      # return associated pdb with finest resolution
      pdb = targets[0][7]

      # close connection 
      cur.close()
      conn.close()

    return render_template('target_panel.html', targets=targets, molecules=molecules, pdb=pdb)



# download molecules associated to target
@app.route('/apdb/home/browse-targets/download', methods=['GET', 'POST'])

def target_molecules_download():

  # get action
  if request.method == 'POST':

    # get associated molecules convering string into a list of tuples
    target_molecules = ast.literal_eval(request.form.get('molecules_download'))
    # get current symbol 
    symbol = request.args.get('symbol')

    # create output dataframe
    target_molecules_df = pd.DataFrame(target_molecules, columns=['CID', 'Chemical Name', 'Molecular Formula', 'Canonical SMILES'])
  
  # return file
  return send_file(
    io.BytesIO(target_molecules_df.to_csv(index=False, sep=";", encoding='utf-8').encode()),
    as_attachment=True,
    download_name='Target_'+symbol+'_MoleculesTable.csv',
    mimetype='text/csv')



# browse descriptors 
@app.route('/apdb/home/browse-descriptors', methods=['GET'])  

def descriptor_browse():

  return render_template('descriptors_overview.html')


# download descriptor table
@app.route('/apdb/home/browse-descriptors/download', methods=['GET']) 

def descriptor_download():

  # get action
  if request.method == 'GET':

    # get element to filter 
    descriptor = request.args.get('descriptor', type = str)

    # path to read
    path = os.getcwd() + "/psql_db/Tables"

    # read fingerprints bits
    if descriptor == 'FB': 
      filename = 'FPBitsTable.csv'
      df = pd.read_csv(path + '/' + filename, index_col=0)  
      # generate output csv
      csv = df.to_csv()
      response = make_response(csv)
      cd = 'attachment; filename='+filename
      response.headers['Content-Disposition'] = cd 
      response.mimetype='text/csv'

    # read fingerprints counts
    if descriptor == 'FC': 
      filename = 'FPCountsTable.csv'
      df = pd.read_csv(path + '/' + filename, index_col=0)  
      # generate output csv
      csv = df.to_csv()
      response = make_response(csv)
      cd = 'attachment; filename='+filename
      response.headers['Content-Disposition'] = cd 
      response.mimetype='text/csv'

    # read molecular descriptors
    if descriptor == 'MD': 
      filename = 'MolecularDescriptorsTable.csv'
      df = pd.read_csv(path + '/' + filename, index_col=0,  low_memory=False)  
      # generate output csv
      csv = df.to_csv()
      response = make_response(csv)
      cd = 'attachment; filename='+filename
      response.headers['Content-Disposition'] = cd 
      response.mimetype='text/csv'

    # read quantum properties
    if descriptor == 'QP': 
      filename = 'QuantumPropertiesTable.csv'
      df = pd.read_csv(path + '/' + filename, index_col=0)  
      # generate output csv
      csv = df.to_csv()
      response = make_response(csv)
      cd = 'attachment; filename='+filename
      response.headers['Content-Disposition'] = cd 
      response.mimetype='text/csv'

    # return file 
    return response



# browse similarities
@app.route('/apdb/home/browse-similarities', methods=['GET'])

def similarity_browse():

  # get action
  if request.method == "GET":

    # connect to db to get molecules ids 
    conn = get_db_connection()
    cur = conn.cursor()
    # execute query 
    cur.execute("SELECT cid, inchikey FROM molecule_information;")

    # get list of ids values
    molecule_ids = list(itertools.chain(*cur.fetchall()))
    
    return render_template('similarity_panel.html', molecule_ids=molecule_ids)



# download embedding model 
@app.route('/apdb/home/browse-similarities/download', methods=['GET'])

def model_download():

  # get action 
  if request.method == "GET":

    # get model name 
    model_name = request.args.get('model', type = str)
 
    # set embedding models path
    path = os.getcwd() + "/pollutants_db_app/static/models/zip/"
    model_files =  os.listdir(path)

   # set filename
    if model_name == "FB":
      filename = [m for m in model_files if model_name in m][0]
    if model_name == "FC":
      filename = [m for m in model_files if model_name in m][0]
    if model_name == "MD":
      filename = [m for m in model_files if model_name in m][0]
    if model_name == "QP":
      filename = [m for m in model_files if model_name in m][0]

    # return file 
    return send_from_directory(path, filename, as_attachment=True)



# browse similar molecules
@app.route("/apdb/home/browse-similarities/panel", methods=['GET', 'POST'])  

def similarity_panel_browse(): 

  # get action  
  if request.method == 'GET':

    # get cid of the selected molecule 
    molecule_id = request.args.get('molecule_id', type = str)
    # get similarity threshold
    threshold = request.args.get('similarity_thr', type = float)

    # connect to db 
    conn = get_db_connection()
    cur = conn.cursor()

    # execute query by cid or inchikey
    if molecule_id.isnumeric():
      cur.execute("SELECT * FROM molecule_information WHERE cid = %s", (molecule_id,))
      molecule = list(itertools.chain(*cur.fetchall()))
      molecule_cid = molecule[1]

    else:
      cur.execute("SELECT * FROM molecule_information WHERE inchikey = %s", (molecule_id,))
      molecule = list(itertools.chain(*cur.fetchall()))
      molecule_cid = molecule[1]

    # remove quotes from chemical name 
    molecule[0] = molecule[0].strip("'")

    # draw structure from smiles 
    smiles = molecule[4]
    mol = Chem.MolFromSmiles(smiles)
    folder_path = os.path.join(os.getcwd(), "pollutants_db_app/static/tmp_img")
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
      # remove folder and files
      shutil.rmtree(folder_path)
    # create folder  
    os.makedirs(folder_path, exist_ok=True)
    # save image
    Draw.MolToFile(mol, os.getcwd() + "/pollutants_db_app/static/tmp_img/mol.png")
    
    # check if single atom 
    single_atom = False
    # add hydrogens
    mol = Chem.AddHs(mol) 
    if mol.GetNumAtoms() == 1:
      single_atom = True 
    elif mol.GetNumAtoms() == 2:
      # manage 2 identical atoms
      if mol.GetAtoms()[0].GetSymbol() == mol.GetAtoms()[1].GetSymbol():
        single_atom = True       

    # return molecule targets
    cur.execute("SELECT target_symbol FROM target_data WHERE molecule_cid = %s;", (molecule_cid,))
    targets = list(itertools.chain(*cur.fetchall()))

    # remove duplicated values
    if targets:
      targets = ", ".join(list(set(targets)))
    else: targets = None
    
    # set embedding models path
    path = os.getcwd() + "/pollutants_db_app/static/models/"
    model_files = os.listdir(path)
    # remove zip folder
    model_files.remove('zip')

    # check single atom
    if single_atom:
      i=2
      models = models = [m for m in model_files if "Elem" in m]
      models.sort()
    else:
      i=0 
      models = [m for m in model_files if "Elem" not in m]
      models.sort()
       
    # generate model path names and colours
    pnames = [path + p for p in models]
    colours = ['#D04CF4', '#724CF4', '#45DA3E', '#F4D34C']

    # return most similar molecules 
    df_similar = pd.DataFrame()
    for PATH in pnames:
      # load model
      model = Word2Vec.load(PATH)

      # get number of molecules
      cur.execute("SELECT COUNT(*) FROM molecule_information")
      n=list(itertools.chain(*cur.fetchall()))[0]

      # check if key exists
      try:
        similar = [item for item in model.wv.most_similar(str(molecule_cid), topn=n) if item[1] > threshold]
        # at least two similar molecules
        thr=threshold
        while (len(similar) < 2 and thr > 0.75):  
          # decrease similarity threshold
          thr-=0.01
          similar = [item for item in model.wv.most_similar(str(molecule_cid), topn=n) if item[1] > thr]
        # output dataframe
        df = pd.DataFrame(similar)     

      except KeyError:  
        continue
      
      # define columns
      df.columns=['similar_cid','measure']
      df['model'] = i
      df['colour'] = colours[i]
      i+=1

      # output dataframe
      df_similar = pd.concat([df_similar, df])
      # round similarity values
      df_similar['measure'] = df_similar['measure'].round(3)

    top_similar = []
    # check if dataframe is empty
    if df_similar.empty:
      alert_message = "No similar molecules found. Try with another compound."
    else: 
      # check if maximum similarity is lower than the initial threshold and raise alert
      if (df_similar['measure'].max() < threshold):
        alert_message = "0 items found. Showing most similar molecules with closest threshold:"
      # retrieve the number of records found
      else: alert_message="{} records found.".format(len(df_similar['similar_cid'].unique()))

      # sort similar molecules by frequency and average similarity value across spaces 
      similar_freq = pd.DataFrame(df_similar.groupby('similar_cid')['measure'].mean())
      similar_freq['count'] = df_similar.groupby('similar_cid')['similar_cid'].count()
      similar_freq.sort_values(by=['count', 'measure'], ascending=[False, False], inplace=True)
  
      for i in range(len(similar_freq)):
        # get chemical name and canonical smiles
        cur.execute("SELECT chemical_name, canonical_smiles FROM molecule_information WHERE cid = %s;", (int(similar_freq.index[i]),))
        similar_info = list(itertools.chain(*cur.fetchall()))
       
       
        # get most frequent molecules 
        tmp_df = df_similar.loc[df_similar['similar_cid'] == similar_freq.index[i]]
        # add missing models 
        idx = pd.MultiIndex.from_product([tmp_df.similar_cid.unique(), np.arange(5)], names=['similar_cid', 'model'])
        out_df = (tmp_df.set_index(['similar_cid', 'model']).reindex(idx).reset_index())

        # add chemical name 
        out_df.loc[:, ['chemical_name', 'canonical_smiles']] = [similar_info[0].strip("'"), similar_info[1]]
        # substitute missing measures with 0.3
        out_df['measure'] = out_df['measure'].fillna(0.3)
        # substitute missing colours with grey
        out_df['colour'] = out_df['colour'].fillna('#787A78')

        # create output list
        top_similar.append(out_df.values.tolist())

    return render_template("molecule_similarity_panel.html", molecule=molecule, targets=targets, top_similar=top_similar, alert_message=alert_message)
  


# download similar molecules 
@app.route('/apdb/home/browse-similarities/panel/download', methods=['GET', 'POST'])

def similar_molecules_download():

  # get action 
  if request.method == 'POST':

    # get current cid 
    molecule_cid = request.args.get('cid', type = str)
    # get similar molecules
    similar_molecules = request.form.get('molecules_download')
    # convert string into a list of tuples 
    similar_molecules = ast.literal_eval(similar_molecules)
    # unlist list of list
    similar_molecules = [item for sublist in similar_molecules for item in sublist]

    # substitute codes with model names 
    for item in similar_molecules:
      if item[1] == 0:
        item[1] = 'Fingerprint Bits'
      elif item[1] == 1:
        item[1] = 'Fingerprint Counts'
      elif item[1] == 2:
        item[1] = 'Molecular Descriptors'
      elif item[1] == 3:
        item[1] = 'Quantum Properties'
      # substitute 0.3 measures with NaN
      if item[2] == 0.3:
        item[2] = np.nan
      # remove color information 
      del item[3]  

    # output df
    similar_molecules_df = pd.DataFrame(similar_molecules, columns=['CID', 'Embedding Model', 'Similarity Measure', 'Chemical Name', 'Canonical SMILES'])
    
    # sort columns and drop rows containing nan values 
    similar_molecules_df = similar_molecules_df[['CID', 'Chemical Name', 'Canonical SMILES', 'Embedding Model', 'Similarity Measure']].dropna()

    # return file
    return send_file(
    io.BytesIO(similar_molecules_df.to_csv(index=False, sep=";", encoding='utf-8').encode()),
    as_attachment=True,
    download_name='SimilarMolecules_'+molecule_cid+'.csv',
    mimetype='text/csv')
  
  # get action
  elif request.method == "GET":
    
    # get current cid 
    molecule_cid = request.args.get('cid', type = str)

    # set sdf files path name
    path = os.getcwd() + "/pollutants_db_app/static/sdf_files/"
    # find filename with current cid 
    filename = [i for i in os.listdir(path) if molecule_cid in i.split('_')[:-1]]

    # return file
    return send_from_directory(path, filename[0], as_attachment=True)



# browse statistics 
@app.route("/apdb/statistics", methods=['GET'])

def statistics():

  return render_template('statistics.html')



# browse documentation
@app.route("/apdb/documentation", methods=['GET'])

def documentation():

  return render_template('documentation.html')



# browse downloads/contacts  
@app.route("/apdb/downloads-contacts", methods=['GET'])

def contacts():

  return render_template('downloads-contacts.html')



# download database 
@app.route("/apdb/downloads-contacts/db", methods=['GET'])

def db_download(): 

  # get action 
  if request.method == 'GET':

    # get format
    db_format = request.args.get('format', type = str)
 
    # set embedding models path
    path = os.getcwd() + "/psql_db/"
    db_files =  os.listdir(path)

    # set filename
    if db_format == "sql":
      filename = [file for file in db_files if ".sql" in file][0]
    elif db_format == "zip":
      filename = [file for file in db_files if ".zip" in file][0]

    # return file 
    return send_from_directory(path, filename, as_attachment=True)
  

# entry point
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
