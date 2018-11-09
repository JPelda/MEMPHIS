=======
MEMPHIS
=======

Methodology to evaluate and map the potential of waste heat from sewage water by using internationally available open data. MEMPHIS enables you to build up a sewage system generically by using open data. The algorithm shall help to ease the implementation of waste heat from sewage systems identifying suitable locations for waste heat exploitation from sewer.

* `Blog <http://blogs.hawk-hhg.de/memphis/>`__
* `MEMPHIS GitHub repository <https://github.com/JPelda/memphis>`__
* `MEMPHIS documentation and manual <https://memphis.readthedocs.io/en/latest/>`__

Requirements
============

memphis 0.1.0 requires

* Python >= 3.5

MEMPHIS was developed by using `anaconda <https://www.anaconda.com/distribution/>`__ as python distribution 

Clone the repository and run the environment.yml via 

.. code-block:: console

	$ conda env create -f environment.yml

Getting Started
===============
First of all you have to design a config-file for your city. It has the information to your database containing all gis files necessary. For examples, see the config-files (goettingen.ini) in the repository.


Authors
=======

* **Johannes Pelda** - *Initial work* - `on github <https://github.com/JPelda>`__

See also the list of `contributors <https://github.com/JPelda/memphis/contributors>`__ who participated in this project.

License
=======

This project is licensed under GNU General Public License v3.0 - see the LICENSE.txt file for details

Acknowledgments
===============

* Many thanks to the International Energy Agency (IEA) who are funding this research within the Technology Collaboration Programme on District Heating and Cooling including Combined Heat and Power named ANNEX XII. The research is about a methodology to evaluate and map the potential of waste heat from sewage water by using internationally available open data (MEMPHIS). It focuses on waste heat from small and medium industries as well as sewage networks and elaborates a tool to map potentials spatially. The project team consists of AIT Austrian Institute of Technology GmbH, Building Research Establishment Limited (BRE) and the University of Applied Sciences and Arts (HAWK) in Göttingen. The project is led by HAWK.
* In addition, many thanks to the Göttinger Entsorgungsbetriebe (GEB) for supporting the project with their technical knowledge and providing their GIS data.
* Thanks to the open-source community, who provide professional tools and helped with programming challenges. Their work enables the project results to be freely distributed and utilized without costs.


