// generate target pdb structure 
$(document).ready(function(){

    // get symbol for 3dmolviewer
    var symbol = document.getElementById('3dmolviewer_UNIQUEID').getAttribute('value');

    // check if exists
    if (symbol != "NULL") {
    
      // create pdb view
      viewer_UNIQUEID = $3Dmol.createViewer($("#3dmolviewer_UNIQUEID"), {backgroundColor:"white"});
      $3Dmol.download("pdb:"+symbol, viewer_UNIQUEID, {}, function() {
        viewer_UNIQUEID.setStyle({"cartoon": {"color": "spectrum"}});
        viewer_UNIQUEID.render();
      
      // display 3dmolviewer
      document.getElementById('3dmolviewer_UNIQUEID').style.display = "block";
      // set download attributes
      document.getElementById('pdb_download').setAttribute('href' ,'https://files.rcsb.org/download/'+symbol+'.pdb')
      })
    } else {

      // display alphafold block
      document.getElementById('alphafold').style.display = "block";
      // hide download attributes
      document.getElementById('download_header').style.display = "none";
      document.getElementById('pdb_download').style.display = "none";
    }
  });
