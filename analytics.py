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
        #self.varieties = singles + 11 - singles/10
        #self.transition_matrix = ([[0 for x in range(self.varieties)] for y in range(self.varieties)])
        self.modified_transition = 0
        
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
                
                #The 
                counter += 10
                self.rate += 0.005
            #self.transition_matrix[x][x] -= 1
        #for x in range(self.varieties - 1):
        #    self.modified_transition
        #for x in range(self.varieties):
        #    self.transition_matrix[0][x] += 1
            
        #self.transition_matrix[-1][-1] = -1
            
        self.modified_transition = numpy.array(self.transition_matrix)
        for x in range(self.varieties - 1):
            self.modified_transition[x][x] -= 1
        for x in range(self.varieties):
            self.modified_transition[0][x] += 1
        self.modified_transition[-1][-1] = -1
        self.rate = self.baserate
        
        return numpy.linalg.inv(self.modified_transition)[:,0]
    
    #For each pull variety, this function calculates the distribution of 5* units within that pull
    def pull_distribution(self):
        pull_matrix = ([[0 for x in range(11)] for y in range(self.varieties)])
        rate = self.baserate
        pullcount = 0
        for x in range(self.varieties - 1):
            if(x < self.singles):
                thiscount = 1
            else:
                thiscount = 10
            for y in range(11):
                pull_matrix[x][y] = binom_dist(thiscount,rate,y)
                
            pullcount += thiscount
            if(thiscount >= 10 or pullcount % 10 == 0):
                rate += 0.005
        pull_matrix[-1][0] = 0
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
