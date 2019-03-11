"""Hard sphere monte carlo simulation"""
import numpy as np
from voronoi import Colloid_Periodic_Voronoi

class Colloid_Monte_Carlo:


    def __init__(self):
        """Read input file and set up regular lattice of colloid particles"""

        self.read_input_file()
        self.regular_lattice()


    def read_input_file(self):
        """Read sample properties and monte carlo parameters"""

        # Read parameters
        with open('./monte_carlo.inpt','r') as f:
            f.readline()
            self.output_prefix = f.readline().split()[0]
            f.readline()
            f.readline()
            self.n = int(f.readline().split()[0]) # Number of particles
            self.sigma = float(f.readline().split()[0]) # Particle radius
            self.phi = f.readline().split()[0] # Packing fraction
            f.readline()
            f.readline()
            self.random_seed = int(f.readline().split()[0])
            self.mc_moves = int(f.readline().split()[0])
            self.mc_max_trial_distance = float(f.readline().split()[0])

        # Initialise additional parameters
        self.diameter_sq = (2.0*self.sigma)**2
        if self.phi == 'max':
            self.phi = np.pi/(2.0*np.sqrt(3.0))
        else:
            self.phi = float(self.phi)
        self.mc_max_trial_distance *= self.sigma


    def regular_lattice(self):
        """Set up colloid particles on regular hexagonal lattice at given packing fraction"""

        # Calculate distances between particles on regular lattice and simulation box size
        dim = int(np.sqrt(self.n))
        sf = np.sqrt(np.pi/(2.0*np.sqrt(3.0)*self.phi))
        dx = self.sigma*2.0*sf
        dy = self.sigma*np.sqrt(3.0)*sf
        self.box_size = np.array([dim*dx,dim*dy])

        # Set up regular hexagonal lattice
        crds = np.zeros((dim,dim,2),dtype=float)
        x_0 = np.arange(0,dim)*dx
        x_1 = x_0+0.5*dx
        y = np.arange(0,dim)*dy
        for i in range(dim):
            if i%2==0:
                crds[i,:,0] = x_0
            else:
                crds[i,:,0] = x_1
            crds[i,:,1] = y[i]
        self.crds = np.reshape(crds,(self.n,2))


    def monte_carlo(self):
        """Perfrom Monte Carlo simulation"""

        # Initialise Mersenne-Twister random number generator
        self.random_generator = np.random.RandomState(self.random_seed)

        # Initialise Monte Carlo progress
        self.mc_acceptance = 0

        # Perform required moves
        for i in range(self.mc_moves):
            self.monte_carlo_move()
            print(i,self.mc_acceptance/(i+1))

        for i in range(self.n-1):
            ci=self.crds[i,:]
            for j in range(i+1,self.n):
                cj=self.crds[j,:]
                dx=ci[0]-cj[0]
                dy=ci[1]-cj[1]
                if(dx<-self.box_size[0]*0.5): dx+=self.box_size[0]
                elif(dx>self.box_size[0]*0.5): dx-=self.box_size[0]
                if(dy<-self.box_size[1]*0.5): dy+=self.box_size[1]
                elif(dy>self.box_size[1]*0.5): dy-=self.box_size[1]
                dd=np.sqrt(dx*dx+dy*dy)
                if(dd<self.sigma*2):
                    print(i,j,dd)


    def monte_carlo_move(self):
        """Single Monte Carlo displacement move"""

        # Select random particle
        particle = self.random_generator.randint(0,self.n)

        # Get random displacement and trial coordinate
        delta = self.random_generator.uniform(0.0,self.mc_max_trial_distance,size=2)
        prev_crd = np.zeros(2,dtype=float)
        prev_crd[:] = self.crds[particle,:]
        crd = prev_crd + delta
        # Account for periodic boundary
        if crd[0] < 0.0:
            crd[0] += self.box_size[0]
        elif crd[0] > self.box_size[0]:
            crd[0] -= self.box_size[0]
        if crd[1] < 0.0:
            crd[1] += self.box_size[1]
        elif crd[1] > self.box_size[1]:
            crd[1] -= self.box_size[1]
        self.crds[particle,:] = crd

        # Calculate distances to other particles, applying minimum image convention
        dx = self.crds[:,0] - crd[0]
        dy = self.crds[:,1] - crd[1]
        dx[dx<-self.box_size[0]*0.5] += self.box_size[0]
        dx[dx>self.box_size[0]*0.5] -= self.box_size[0]
        dy[dy<-self.box_size[1]*0.5] += self.box_size[1]
        dy[dy>self.box_size[1]*0.5] -= self.box_size[1]
        d_sq = dx*dx+dy*dy

        # Accept if does not violate overlap condition
        if np.sum(d_sq<self.diameter_sq)==1:
            self.mc_acceptance += 1
        else:
            self.crds[particle,:] = prev_crd


    def analysis(self):
        """Construct voronoi diagram and perform network analysis"""

        voronoi = Colloid_Periodic_Voronoi(crds=self.crds,box_size=self.box_size)
        voronoi.calculate_voronoi()
        voronoi.network_analysis()
        print(voronoi.k)
        print(voronoi.p_k)
        print(voronoi.var,voronoi.r)
        voronoi.write()

if __name__ == "__main__":
    mc = Colloid_Monte_Carlo()
    mc.monte_carlo()
    mc.analysis()