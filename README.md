##  APDB: a database on air pollutants characterization and similarity prediction

**APDB** is a publicly available online database which improves our knowledge of the existing pollutant molecules, providing an in-depth insight into their physicochemical, structural and quantum properties. The collection of pollutant molecular structures together with all the chemical characteristics and 
descriptors provided in **APDB**, offers scientists a unique resource for a wide view of the biochemical aspects of pollutant toxicity mechanisms.

**APDB** is available at: http://apdb.di.univr.it 

### Local Setup

The APDB web application is currently available **locally** due to server maintenance and related services. Follow the steps below to run the app and access all its functionalities:

**1. Clone the repository**
```bash
git clone https://github.com/InfOmics/APDB
cd APDB/Flask
```

**2. Start the app with Docker Compose**
```bash
docker-compose up --build -d
```

**3. Access the app**

Open your browser at: http://localhost:5000

**Note**: You will be automatically redirected to `/apdb/home`. 

**4. Stopping the app**
```bash
docker-compose down
```
