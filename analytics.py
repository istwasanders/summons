import numpy
import numpy.linalg
import math

def binom_coef(n,k):
    try:
        return math.factorial(n) / (math.factorial(k) * math.factorial(n-k))
    except:
        return 0

#Calculate binomial distribution
#x - number of successes
#t - number of trials
#r - success rate
def binom_dist(t,r,x=None):
    if x == None:
        results = []
        for y in range(t+1):
            results.append(binom_coef(t,y) * (r**y) * ((1-r)**(t-y)))
        return results
    else:
        return binom_coef(t,x) * (r**x) * ((1-r)**(t-x))

class SummonMatrix:
    def __init__(self, singles, baserate):
        self.baserate = baserate
        self.rate = baserate
        self.singles = singles
        self.modified_transition = 0
        
        #Compute summon varieties, and set up the framework for the transition matrix
        rate = baserate
        pulls = 0
        self.varieties = 0
        while rate <= 0.091:
            self.varieties += 1
            
            if(pulls < singles):
                pulls += 1
                if(pulls % 10 == 0):
                    rate += 0.005
            else:
                pulls += 10
                rate += 0.005
                
        self.transition_matrix = ([[0 for x in range(self.varieties)] for y in range(self.varieties)])
    #What is being called a "Variety" is how many different kinds of pulls there are
    #For example:
    #   the first single summon after a pity break is one variety,
    #   the fifth single summon after one rate up is another variety,
    #   the second tenfold summon is another variety, and so on
    #What this function does is returns the long-term probability distribution of
    #each pull variety
    def variety_distribution(self):
        #First step in calculating variety distribution is to set up a matrix of transitional state probabilities
        #This matrix contains the probabilities of pity breaks for each pull
        self.transition_matrix[0][-1] = 1
        
        #No units have been "summoned" yet
        counter = 0
        for x in range(self.varieties - 1):
            #First fill in the matrix for single summons
            if(x < self.singles):
                #Probabilities for single summons are simple, either you get a 5* or not
                self.transition_matrix[x+1][x] = 1 - self.rate      #Probability of no 5*
                self.transition_matrix[0][x]   = self.rate          #Probability of yes 5*
                
                #One more "summon" has been performed.  Increment summon count and, if necessary, the 5* rate
                counter += 1
                if(counter % 10 == 0):
                    self.rate += 0.005
            
            #Next fill in the matrix for tenfold summons
            else:
                #Tenfold summons are a bit more complicated, the probability of no pity break is
                #the probability that none of the ten summoned units are 5*
                #The probability of a pity break is the probability that at least one of the
                #summoned units is a 5*
                self.transition_matrix[x+1][x] = (1-self.rate) ** 10                #Probability of no 5*
                self.transition_matrix[0][x]   = 1 - self.transition_matrix[x+1][x] #Probability of yes 5*
                
                #The pity rate always goes up after a tenfold
                counter += 10
                self.rate += 0.005
        
        #Set up a modified transition matrix to calculate the variety distribution
        self.modified_transition = numpy.array(self.transition_matrix)
        
        #Calculations for variety distributions are as follows:
        #Preliminary information:
        #   The matrix A represents the transition matrix
        #   We want to determine long term summon results
        #   The vector x_n represents pull distribution for the nth summon
        #
        #   Performing a summon is represented by multiplying A*x
        #In order to determine long term summon results (or x_infinity):
        #   We wish to find when x_(n+1)
        #   This is equivalent to solving   A*x = I*x
        #   Which we can rework into (A-I)*x = 0
        #   We have a secret weapon, which is that the sum of elements in x should be 1
        for x in range(self.varieties):
            #This line handles (A-I)
            self.modified_transition[x][x] -= 1
            
            #This line uses our secret weapon
            self.modified_transition[0][x] += 1
            
        self.rate = self.baserate
        
        #Invert the matrix to solve the system
        return numpy.linalg.inv(self.modified_transition)[:,0]
    
    #For each pull variety, this function calculates the distribution of 5* units within that pull
    def pull_distribution(self):
        #Each time the summon button is pressed, between 0 and 10 5* units are summoned
        pull_matrix = ([[0 for x in range(11)] for y in range(self.varieties)])
        
        #Start at base 5* rate and 0 units summoned this pity reset
        rate = self.baserate
        pullcount = 0
        
        #Fill out the distribution of 5* pulls at various pity rates
        for x in range(self.varieties - 1):
            if(x < self.singles):
                thiscount = 1
            else:
                thiscount = 10
            for y in range(11):
                #Pull distribution follows the binomial distribution at the associated pity rate
                #With 1 trial for a single summon, and 10 trials for a tenfold summon
                pull_matrix[x][y] = binom_dist(thiscount,rate,y)
                
            pullcount += thiscount
            #Increment the pity either after 10 pulls or at the appropriate single summon
            if(thiscount >= 10 or pullcount % 10 == 0):
                rate += 0.005
                
        #The pull with a guaranteed 5* is a little different
        #When guaranteed 5*, a pull has probability 0 of having 0 5*
        pull_matrix[-1][0] = 0
        
        #The number of 5* pulled follows the binomial distribution with 9 trials
        for y in range(11):
            pull_matrix[-1][y] = binom_dist(9,rate,y-1)
            
        return numpy.array(pull_matrix)
        
def main():
    #M = SummonMatrix(100,0.04)
    #v = M.variety_distribution()
    #p = M.pull_distribution()
        
    def compile_pulls(MS,ps,vs):
        #Multiply the relative frequencies for each pull by the probability of that pull
        #And by the number of 5* received in that pull
        for x in range(len(ps)):
            ps[x] = numpy.multiply(ps[x],vs[x])
            for y in range(len(ps[0])):
                ps[x][y] = numpy.multiply(ps[x][y],y)
        
        #Weight the tenfold summons appropriately
        for x in range(len(vs)):
            if x >= MS.singles:
                vs[x] *= 10
                
        return ps.sum()/vs.sum()

    M = SummonMatrix(20,0.04)
    v = M.variety_distribution()
    p = M.pull_distribution()
    print compile_pulls(M,p,v)
    
if __name__ == '__main__':
    main()
