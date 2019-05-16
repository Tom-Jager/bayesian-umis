# bayesian-umis
A Bayesian inference engine for UMIS structured MFA systems

## Contents

* bayesumis
    * umis_diagram.py
        * Module containing UmisDiagram class, Pythonic implementation of storing a UMIS diagram
    * umis_data_models.py
        * Module containing Pythonic implementations of UMIS component objects
    * umis_math_model.py
        * Module containing UmisMathModel class, object that constructs the mathematical model from the UmisDiagram and its helper classes
* stafdb  
    * db_writer_helpers.py
        * Module to write records to stafdb csv files
    * graedal_records_writer.py
        * Script to write data records for graedal test into stafdb
     * staf_factory.py
        * Module containing classes that build stocks, flows and processes from stafdb records
     * stafdb_access_objects.py
        * Module that obtains records from stafdb csv files by their id
     * test_records_writer.py
        * Script to write some test records into stafdb
* testhelper
    * posterior_plotters.py
        * Module that has methods for taking a stock or flow and plotting the posterior distribution for them, main function is the display_parameters function
     * test_helper.py
         * Module containing DbStub, class that acts as a fake stafdb and generates stock, flow, process objects
     * umis_builders.py
         * Module that contains function for building test umis diagrams
         
         
## Tests
Tests can be run by running all cells in the jupyter notebooks
