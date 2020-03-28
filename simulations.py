import random
import sys,getopt

f = open("log.txt","w")
f.close()

class Summons:
    def __init__(self, baserate):
        self.baserate = baserate
        self.rate = baserate
        self.total_summons = 0
        self.fivestar = 0
        self.this_summons = 0
        self.tenfoldlog = [[0 for x in range(12)] for y in range(11)]
        
    #When performing a single summon...
    def single(self):
        #Increment total summon count
        self.total_summons = self.total_summons + 1
        result = random.random()
        #100 previous summons guarantees a 5*, or from random pulling
        if (result <= self.rate) or (self.this_summons >= 100):
            #Reset pity rate and pity rate counter
            self.rate = self.baserate
            self.this_summons = 0
            #Increment 5* count
            self.fivestar = self.fivestar + 1
            #f = open("log.txt","a+")
            #f.write("%12d\t%12d\t%12f\t%12d\t%12f\n" % (self.total_summons, self.this_summons, self.rate, self.fivestar, result))
            #f.close()
            #Indicate that a 5* has been pulled
            return 1
        else:
            #Increment pity rate counter
            self.this_summons = self.this_summons + 1
            if(self.this_summons % 10 == 0):
                #Increment pity rate after 10 summons
                self.rate = self.rate + 0.005
            #Indicate that no 5* was pulled
            #f = open("log.txt","a+")
            #f.write("%12d\t%12d\t%12f\t%12d\t%12f\n" % (self.total_summons, self.this_summons, self.rate, self.fivestar, result))
            #f.close()
            return 0
    
    def tenfold(self):
        row = self.this_summons / 10
        
        #We have performed ten summons
        self.total_summons = self.total_summons + 10
        
        #Generate random for each of the ten pulls
        results = [random.random() for x in range(10)]
        
        #100 previous summons guarantees a 5*
        if(self.rate >= 0.09):
            results[0] = 0
        
        #count the number of 5* that were summoned
        five_star_count = 0
        for result in results:
            if(result <= self.rate):
                five_star_count = five_star_count + 1
        
        #Update total 5* count
        self.fivestar = self.fivestar + five_star_count
        
        column = five_star_count
        
        self.tenfoldlog[row][column] += 1
        self.tenfoldlog[row][11] += 1
        
        #f = open("log.txt","a+")
        #f.write("%12d\t%12d\t%12f\t%12d\n" % (self.total_summons, self.this_summons, self.rate, self.fivestar))
        #f.write("%s\n" % str(results))
        #f.close()
        
        if(five_star_count > 0):
            #Reset pity rate and pity rate counter
            self.rate = self.baserate
            self.this_summons = 0
            #Indicate that at least one 5* has been pulled
            return 1
        else:
            #Increment pity rate counter
            self.this_summons = self.this_summons + 10
            #Increment pity rate
            self.rate = self.rate + 0.005
            #Indicate that no 5* was pulled
            return 0
            
def main(argv):
    try:
        opts,args = getopt.getopt(argv,"s:r:t:",["singles=","baserate=","total="])
    except getopt.GetoptError:
        print "AAAAAAAAAA"
        sys.exit(2)
        
        
    singles = 0
    rate = 0.04
    total = 10000
    
    for opt,arg in opts:
        if opt == '-s':
            singles = int(arg)
        if opt == '-r':
            rate = float(arg)
        if opt == '-t':
            total = int(arg)
            
    summons = Summons(rate)
    summon_presses = 0
    while(summons.total_summons < total):
        summon_presses += 1
        if(summons.this_summons < singles):
            summons.single()
        else:
            summons.tenfold()
            
    print "Summons Spent: " + str(summons.total_summons)
    print "Summon Press:  " + str(summon_presses)
    print "5*s Summoned:  " + str(summons.fivestar)
    
    print "Average: " + str(float(summons.total_summons)/summons.fivestar)
    print "5* Rate: " + str(float(summons.fivestar)/summons.total_summons)
    
    for row in summons.tenfoldlog:
        print row
    
    '''
    x = 0
    for row in summons.tenfoldlog:
        x += row[-1]
        print row
        print x
        try:
            print float(row[0])/row[-1]
        except:
            pass
            
    for row in summons.tenfoldlog:
        print float(row[-1])/summon_presses
    '''

if __name__ == "__main__":
    main(sys.argv[1:])