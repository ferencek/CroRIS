# --------------------------------------------------
# Configuration
# --------------------------------------------------

# Collaboration (if set to None, will be taken from the input BibTeX file)
collaboration = 'CMS'

# Some always used generic keywords
keywords = ['High energy physics', 'Experimental particle physics', 'LHC', 'CMS']

# Institutions
# CroRIS_ID    Name
# 21           Fakultet elektrotehnike, strojarstva i brodogradnje u Splitu / Faculty of Electrical Engineering, Mechanical Engineering and Naval Architecture in Split
# 66           Institut Ruđer Bošković / Ruđer Bošković Institute
# 79           Prirodoslovno-matematički fakultet, Zagreb / Faculty of Science in Zagreb
# 114          Prirodoslovno-matematički fakultet u Splitu / Faculty of Science in Split
# 288          Sveučilište u Rijeci, Fakultet za fiziku / University of Rijeka, Faculty of Physics

# Authors from Croatian institutions (past and present)
authors = {
#   Author name       :  Author full name                     CroRIS_ID              Institution_ID
    'Antunovic, Z'    : ['Antunović, Željko',                 18440,                 114], # retired
    'Bargassa, P'     : ['Bargassa, Pedrame',                 46796,                 66],
    'Brigljevic, V'   : ['Brigljević, Vuko',                  17389,                 66],
    'Ceci, S'         : ['Ceci, Saša',                         3333,                 66],
    'Chitroda, B'     : ['Chitroda, Bhakti Kanulal',          37350,                 66],
    'Duric, S'        : ['Đurić, Senka',                      27211,                 66], # inactive
    'Ferencek, D'     : ['Ferenček, Dinko',                   32647,                 66],
    'Giljanovic, D'   : ['Giljanović, Duje',                  34122,                 21], # inactive
    'Godinovic, N'    : ['Godinović, Nikola',                 14717,                 21],
    'Jakovcic, K'     : ['Jakovčić, Krešimir',                 3340,                 66],
    'Kadija, K'       : ['Kadija, Krešo',                     17565,                 66], # retired
    'Kovac, M'        : ['Kovač, Marko',                      30446,                 114],
    'Lelas, D'        : ['Lelas, Damir',                      27649,                 21],
    'Lelas, K'        : ['Lelas, Karlo',                      27596,                 21], # now at Faculty of Textile Technology, University of Zagreb
    'Luetic, J'       : ['Luetić, Jelena',                    30615,                 66], # inactive
    'Majumder, D'     : ['Majumder, Devdatta',                30615,                 66], # inactive
    'Mekterovic, D'   : ['Mekterović, Darko',                  2640,                 66], # now at UniRi
    'Mesic, B'        : ['Mesić, Benjamin',                   33599,                 66], # inactive
    'Micanovic, S'    : ['Mićanović, Saša',                   21402,                 66], # now at UniRi
    'Mishra, S'       : ['Mishra, Saswat',                    35489,                 66],
    'Morovic, S'      : ['Morović, Srećko',                   21401,                 66], # now at UCSD
    'Petkovic, A'     : ['Petković, Andro',                   37949,                 114],
    'Polic, D'        : ['Polić, Dunja',                        251,                 21], # inactive
    'Puljak, I'       : ['Puljak, Ivica',                      4129,                 21],
    'Roguljic, M'     : ['Roguljić, Matej',                   34885,                 66], # now at JHU
    'Starodumov, A'   : ['Starodumov, Andrey',                46806,                 66], # Andrey's name written as 'Andrei' in the CMS database
    'Sudic, L'        : ['Sudić, Lucija',                      None,                 66], # inactive (djevojačko / maiden Tikvica)
    'Tikvica, L'      : ['Tikvica, Lucija',                    None,                 66], # inactive
    'Susa, T'         : ['Šuša, Tatjana',                      4291,                 66],
    'Sculac, A'       : ['Šćulac, Ana',                        None,                 21],
    'Sculac, T'       : ['Šćulac, Toni',                      33266,                 114]
}

# Info that is in common to all publications
# (see https://wiki.srce.hr/display/CRORIS/CROSBI+API for more info)
pub_common = {
    "tip": 760,
    "status": 965,
    "suradnja_medjunarodna": "D",
    "recenzija": {
        "status": 900,
        "vrsta": 903
    },
    "poveznice": [
        {
            "url_vrsta": 990,
            "url": "https://doi.org/"
        }
    ]
}
# Institution template dictionary
inst_dict = {
    "croris_id": None,
    "mbu": None,
    "uloga": 941
}
# Project template dictionary
proj_dict = {
    "croris_id": None,
    "uloga": 1020
}

# Currently known journals
journals = {
#   Inspire HEP name    : CroRIS name
    'JHEP'                    : 'The Journal of high energy physics',
    'Phys. Rev. Lett.'        : 'Physical review letters',
    'Eur. Phys. J. C'         : 'European physical journal C : particles and fields',
    'JINST'                   : 'Journal of Instrumentation',
    'Phys. Lett. B'           : 'Physics letters. B',
    'Phys. Rev. C'            : 'Physical review. C',
    'Phys. Rev. D'            : 'Physical review. D',
    'Nature Phys.'            : 'Nature physics',
    'Comput. Softw. Big Sci.' : 'Computing and software for big science',
    'Nucl. Instrum. Meth. A'  : 'Nuclear instruments & methods in physics research. Section A, Accelerators, spectrometers, detectors and associated equipment'
}

# ISSNs for currently known journals
issn = {
#   Journal name        : [ISSN, e-ISSN]
    'JHEP'                    : ['1126-6708', '1029-8479'],
    'Phys. Rev. Lett.'        : ['0031-9007', '1079-7114'],
    'Eur. Phys. J. C'         : ['1434-6044', '1434-6052'],
    'JINST'                   : ['1748-0221', '1748-0221'],
    'Phys. Lett. B'           : ['0370-2693', '1873-2445'],
    'Nature Phys.'            : ['1745-2473', '1745-2481'],
    'Phys. Rev. C'            : ['2469-9985', '2469-9993'],
    'Phys. Rev. D'            : ['2470-0010', '2470-0029'],
    'Comput. Softw. Big Sci.' : ['2510-2036', '2510-2044'],
    'Nucl. Instrum. Meth. A'  : ['0168-9002', '1872-9576']
}

# --------------------------------------------------
