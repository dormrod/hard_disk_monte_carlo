"""Hard binary disc monte carlo simulation"""
import numpy as np
import sys
from voronoi import Colloid_Periodic_Voronoi


class Binary_Colloid_Monte_Carlo:


    def __init__(self):
        """Read input parameters and initialise starting configuration"""

        self.read_input_file()
        self.initial_configuration()


    def read_input_file(self):
        """Read binary colloid sample properties and monte carlo parameters"""

        # Read parameters
        with open('./binary.inpt','r') as f:
            f.readline()
            self.output_prefix = f.readline().split()[0]
            self.output_freq = int(f.readline().split()[0])
            f.readline()
            f.readline()
            self.n = int(f.readline().split()[0]) # Total number of particles
            self.n_proportion = float(f.readline().split()[0]) # Number ratio b/a
            self.sigma_ratio = float(f.readline().split()[0]) # Sigma ratio b/a
            self.phi = float(f.readline().split()[0]) # Total packing fraction
            # self.sigma = float(f.readline().split()[0]) # Particle radius
            # self.phi = f.readline().split()[0] # Packing fraction
            # f.readline()
            # f.readline()
            # self.random_seed = int(f.readline().split()[0])
            # self.mc_moves = int(f.readline().split()[0])
            # self.mc_max_trial_distance = float(f.readline().split()[0])

        # Initialise additional parameters
        self.n_a = int(self.n*self.n_proportion) # Number of a
        self.n_b = self.n-self.n_a # Number of b
        self.sigma_a = 1.0 # Radius of a
        self.sigma_b = self.sigma_ratio*self.sigma_a # Radius of b
        self.sigma_ab = 2.0*np.sqrt(self.sigma_a*self.sigma_b) # Non-additive interaction distance
        self.hd_aa = self.sigma_a*self.sigma_a # Hard disc a-a squared interaction
        self.hd_ab = self.sigma_ab*self.sigma_ab # Hard disc a-b squared interaction
        self.hd_bb = self.sigma_b*self.sigma_b # Hard disc b-b squared interaction
        self.cell_area = ((self.n_a*np.pi*self.sigma_a**2)+(self.n_b*np.pi*self.sigma_b**2))/self.phi # Periodic cell area
        self.cell_length = np.sqrt(self.cell_area) # Periodic cell length
        self.phi_a = (self.n_a*np.pi*self.sigma_a**2)/self.cell_area # Partial packing fractions
        self.phi_b = (self.n_b*np.pi*self.sigma_b**2)/self.cell_area # Partial packing fractions
        self.q = self.phi_b / self.phi
        print('------------------------------------------')
        print('System Properties')
        print('Number of particles: T={}  A={}  B={}'.format(self.n,self.n_a,self.n_b))
        print('Packing fraction: T={}  A={}  B={}'.format(self.phi,self.phi_a,self.phi_b))
        print('Composition: {}'.format(self.q))
        print('------------------------------------------')


    def initial_configuration(self):
        """Set up initial ordered lattice"""

        # Calculate blocks needed to construct lattice
        block_b_capacity = 1
        block_a_capacity = int(np.floor(self.sigma_ratio)**2)
        num_block_b = self.n_b//block_b_capacity
        num_block_a = self.n_a//block_a_capacity
        remainder_block_b = self.n_b%block_b_capacity
        remainder_block_a = self.n_a%block_a_capacity
        total_blocks = int(np.ceil(np.sqrt(num_block_a+num_block_b+remainder_block_a+remainder_block_b))**2)
        spacing_blocks = total_blocks - num_block_a - num_block_b - remainder_block_a - remainder_block_b
        check_area = total_blocks*(2.0*self.sigma_b)**2<self.cell_area

        print('Lattice Construction')
        print('Number of full blocks: A={}  B={}'.format(num_block_a,num_block_b))
        print('Remainder blocks: A={}  B={}'.format(remainder_block_a,remainder_block_b))
        print('Spacing blocks: {}'.format(spacing_blocks))
        print('Needed vs required area: N={}  R={}  Check={}'.format(total_blocks*(2.0*self.sigma_b)**2,self.cell_area,check_area))

        if not check_area:
            sys.exit()

        # Arrange blocks
        block_dim = np.sqrt(self.cell_area/total_blocks)
        block_a_crds = np.zeros((block_a_capacity,2))
        block_b_crds = np.zeros((block_b_capacity,2))
        k = 0
        delta = block_dim/np.sqrt(block_a_capacity)
        for i in range(int(np.sqrt(block_a_capacity))):
            for j in range(int(np.sqrt(block_a_capacity))):
                block_a_crds[k,0] = j*delta
                block_a_crds[k,1] = i*delta
                k += 1
        k = 0
        delta = block_dim/np.sqrt(block_b_capacity)
        for i in range(int(np.sqrt(block_b_capacity))):
            for j in range(int(np.sqrt(block_b_capacity))):
                block_b_crds[k,0] = j*delta
                block_b_crds[k,1] = i*delta
                k += 1
        self.crds_a = np.zeros((self.n_a,2))
        self.crds_b = np.zeros((self.n_b,2))
        count_a = 0
        count_b = 0
        count_s = 0
        type = 'a'
        for i in range(int(np.sqrt(total_blocks))):
            for j in range(int(np.sqrt(total_blocks))):
                block_crd = np.array([j*block_dim,i*block_dim])
                if type=='a':
                    block_crds = block_a_crds + block_crd
                    for crd in block_crds:
                        self.crds_a[count_a,:] = crd
                        count_a += 1
                    if count_b < self.n_b:
                        type = 'b'
                    else:
                        type = 's'
                elif type=='b':
                    block_crds = block_b_crds + block_crd
                    for crd in block_crds:
                        self.crds_b[count_b,:] = crd
                        count_b += 1
                    if count_a < self.n_a:
                        type = 'a'
                    else:
                        type = 's'
                else:
                    count_s += 1
        # Check no overlaps in starting configuration
        overlap = False
        for i in range(self.n_a):
            overlap = self.hard_disc_overlap(i,0)
            if overlap:
                break
        for i in range(self.n_b):
            overlap = self.hard_disc_overlap(i,1)
            if overlap:
                break
        print('Overlap: {}'.format(overlap))
        print('------------------------------------------')
        if overlap:
            sys.exit()


    def hard_disc_overlap(self,ref_id,ref_type):
        """Check if any hard-disc overlap between given particle and all others"""

        # Get coordinate of reference particle
        if ref_type == 0:
            ref_crd = self.crds_a[ref_id,:]
            hd_a = self.hd_aa
            hd_b = self.hd_ab
        else:
            ref_crd = self.crds_b[ref_id,:]
            hd_a = self.hd_ab
            hd_b = self.hd_bb

        # Calculate distances to other particles of type a, applying minimum image convention
        dx_a = self.crds_a[:, 0] - ref_crd[0]
        dy_a = self.crds_a[:, 1] - ref_crd[1]
        dx_a[dx_a < -self.cell_length * 0.5] += self.cell_length
        dx_a[dx_a > self.cell_length * 0.5] -= self.cell_length
        dy_a[dy_a < -self.cell_length * 0.5] += self.cell_length
        dy_a[dy_a > self.cell_length * 0.5] -= self.cell_length
        d_sq_a = dx_a * dx_a + dy_a * dy_a

        # Check overlap and return if found
        overlap = False
        if np.sum(d_sq_a < hd_a)>1:
            overlap = True
            return overlap

        # Calculate distances to other particles of type b, applying minimum image convention
        dx_b = self.crds_b[:, 0] - ref_crd[0]
        dy_b = self.crds_b[:, 1] - ref_crd[1]
        dx_b[dx_b < -self.cell_length * 0.5] += self.cell_length
        dx_b[dx_b > self.cell_length * 0.5] -= self.cell_length
        dy_b[dy_b < -self.cell_length * 0.5] += self.cell_length
        dy_b[dy_b > self.cell_length * 0.5] -= self.cell_length
        d_sq_b = dx_b * dx_b + dy_b * dy_b

        # Check overlap
        if np.sum(d_sq_b < hd_b)>1:
            overlap = True

        return overlap


if __name__ == "__main__":
    mc = Binary_Colloid_Monte_Carlo()