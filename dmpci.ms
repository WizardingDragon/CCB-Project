dpd

Title	" Water/surfactant bilayer "
Date	29/11/2019
Comment	" Potato "

State   compositelamella
        Polymers    Lipid   OctoLipid
        Normal      0 0 1
        Centre      0.5
        Thickness   5.0
        Linearise   0
        UpperFraction   0.5 0.5
        Patches     1   1
        Polymerise  0

Bead	H	
    	0.5
    	25	
    	4.5	

Bead	T
    	0.5
    	50	25
    	4.5	4.5	

Bead	W
		0.5
		35	75	25
		4.5	4.5	4.5

Bond	H H	128 0.5
Bond	H T 128 0.5
Bond	T T 128	0.5

BondPair	H T T	20.0	0.0
BondPair	T T T	20.0	0.0

Polymer Water 0.9801083 "  (W)  "
Polymer Lipid 0.00994585 "  (H H (* (T T T T)) H T T T T)  "
Polymer OctoLipid 0.00994585    "  (H H (* (T T T T T T T T T T T T T )) H T T T T T T T T T T T T T )  "
Box			20 20 20			1 1 1
Density		3
Temp		1
RNGSeed		-60112
Lambda		0.5
Step		0.02
Time		1000
SamplePeriod		100
AnalysisPeriod		100
DensityPeriod		1000
DisplayPeriod		100
RestartPeriod		1000
Grid		10 10 256

Analysis
	Type	bilayer
	Times	0 1000
	Polymer Lipid
	Normal	0 0 1
	Slice	256
	Grid	16 16
	Solvent	Water

Command	ToggleBeadDisplay				1    W
Command SetCurrentStateCamera			1    0.5 -0.5 -0.5  0.5 0.5 0.5
Command SetCurrentStateDefaultFormat	1    Paraview

Command	SetTimeStepSize	100	0.01
