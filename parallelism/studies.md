### Studies on Parallelism

- Application to the California Great                                           
   21   Registers](https://arxiv.org/abs/1905.05337): This paper uses Alameda County  
   20   voter registration data from Alameda County between 1932 and 1936 as a record 
   19   linkage case study. There are various theories about which demographic groups 
   18   were most responsible for the large number of voters who changed parties      
   17   during Roosevelt's first term, so this project seeks to test those theories   
   16   against the Alameda County data by matching the records and then observing    
   15   who changed parties (for this reason, they do not use party identification as 
   14   one of the matching fields). The authors observe that, regardless of what     
   13   model you're using (the paper uses the Fellegi-Sunter model with an           
   12   additional penalty term in the likelihood function in order to control the    
   11   number of true matches that are identified, and seeks to estimate the m- and  
   10   u- probabilities), having a full posterior distribution over the parameters   
    9   is preferable to, say, just having maximum likelihood estimates in order to   
    8   characterize your uncertainty about the downstream inferences, and suggest    
    7   sampling from a full Bayesian model for this reason. However, it's often too  
    6   computationally intensive to do MCMC for anything but the smallest data sets. 
    5   So this paper presents a sort of extension to blocking (not literally a type  
    4   of blocking, as the authors point out). Note that the example in the paper is 
    3   a case of "one-to-one" matching -- that is, the special case where you are    
    2   matching two databases that are each assumed to be de-duplicated, so that     
    1   each record from one data set has at most one matching record in the other    
662     one. From my reading, this constraint is not necessary for the logic they've                       
    1   laid out (the technique seems independent of the model you're using), but the 
    2   effeciency gains they observe that makes it possible to run MCMC on larger    
    3   data sets depends on this constraint, because this is the constraint that     
    4   allows them to partition the overall record-linkage matrix into smaller       
    5   blocks that can be optimized in parallel. So, anyways, the method: start by   
    6   doing a coarse round of blocking using whatever method, then use that blocked 
    7   data set to estimate match weights using a cheaper technique (e.g.            
    8   expectation maximization for the Fellegi Sunter model). Then use these match  
    9   weights to further filter the set of record pairs, by setting a threshold and 
   10   zeroing out any weights that are less than the threshold. Having done that,   
   11   you end up with a bunch of connected components that can themselves be        
   12   treated as blocks, and since there can't be links between records in          
   13   different blocks (because of the one-to-one constraint), you can make the     
   14   decisions about which links are true within each block in parallel. That's    
   15   the basic idea, as far as I can tell. There were a few sections of this paper 
   16   that I had to re-read several times because I'm not sure I understood them    
   17   properly, and perhaps that has to do with my interpretation of the method as  
   18   "just" an additional filtering step beyond blocking in order to reduce the    
   19   size of the set of candidate pairs. For instance, the authors claim they are  
   20   able to use all blocked pairs in order to inform their inferences, rather     
   21   than just those that make it through the weighing/thresholding step. I'm      
   22   still working out how that works, and suspect I'll not fully understand until 
   23   I've played with some code. To that end, this paper has an associated [Julia  
   24   package](https://github.com/brendanstats/BayesianRecordLinkage.jl).
