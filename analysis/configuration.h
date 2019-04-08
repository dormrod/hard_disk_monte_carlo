#ifndef BNAHDMC_ANALYSIS_CONFIGURATION_H
#define BNAHDMC_ANALYSIS_CONFIGURATION_H

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include "outputfile.h"
#include "vecf.h"
#include "../voro++/src/voro++.hh"

class Configuration {

private:

    //General variables
    int nCrdSets; //number of sets of coordinates analysed
    int nA, nB, nC; //number of type a, b and total
    double rA, rB; //radius of type a and b
    double cellLen,rCellLen,cellLen_2; //length/reciprocal/half of periodic cell
    VecF<double> xA,yA,xB,yB; //x and y coordinates of particles of type a and b

    //RDF varaibles
    double rdfDelta, rdfMaxSq; //historgram bin widths and square of maximum value
    VecF<double> rdfR, rdfAA, rdfBB, rdfAB, rdfC; //partial radial distribution functions

public:

    //Constructors
    Configuration();
    Configuration(int numA, int numB, double radA, double radB, double cellLength);

    //Member functions
    void setCoordinates(ifstream& xyzFile, Logfile& logfile);
    void setRdf(double delta, double extent);
    void rdf(Logfile& logfile);
    void rdfFinalise(string prefix, Logfile& logfile);
    void voronoi(Logfile& logfile);
};


#endif //BNAHDMC_ANALYSIS_CONFIGURATION_H