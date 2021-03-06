import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    print("=========== link in the page is ===============")
    print(corpus)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print("-------------------------------------------------")
   
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    proability_distribution = dict()
    #get total number of pages
    total_num_of_pages = len(corpus)

    #return the proability that surfer can go back to the exact same page
    p_randomly = 1 / len(corpus) * (1- damping_factor)

    #return the proability that surfer can press link to page i
    if len(corpus[page]) == 0:
        for p in corpus:
            proability_distribution.update({p: p_randomly})

    else:
        proability_distribution.update({page: p_randomly})
        for link in corpus[page]:
            #TODO: if link is duplicate
            p_link = 1/len(corpus[page]) * damping_factor
            proability_distribution.update({link: p_link + p_randomly})
        
    return proability_distribution 


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    sample = None

    #init page rank in 
    for page in corpus:
        pagerank[page] = 0
    
    #iterate n time
    for i in range(n):
        #the first sample should be generated by choising from a page at random
        if sample is None:
            sample = random.choice(list(corpus.keys()))
            print(sample)
        else: # the next sample should be generated from the previous sample based on the previous sample model
            #get the transition model of the previous sample
            trans_model = transition_model(corpus, sample, damping_factor)

            population, weights = zip(*trans_model.items())

            sample = random.choices(population, weights=weights, k =1)[0]

        #update ranking
        pagerank[sample] +=1
    
    #nomamlize the result
    for page in corpus:
        pagerank[page] /= n

    return pagerank

  


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict()  
    new_rank = dict()

    #initial proability
    for page in corpus:
        page_rank[page] = 1 / len(corpus)

    flag = True
    #calculate new rank based on current rank value
    while flag:
      
        for page in page_rank:
            total = 0
            for p in corpus:
                #if current page in other page link
                if page in corpus[p]:
                    total += page_rank[p] / len(corpus[p])
                
                # if page at p has no link at all
                if not corpus[p]:
                    total += page_rank[p] / len(corpus) # assum it has links to all other pages

            #calculate page rank at p (concerning that p can be linked from other pages and chances of hitting p itself)
            new_rank[page] = (1-damping_factor)/ len(corpus) + damping_factor * total
        
        flag = False

        #thersh hold: 0.001 - Pagerank value changes
        for page in page_rank:
            if not math.isclose(new_rank[page], page_rank[page], abs_tol = 0.001):
                flag = True
            
            #assign new values to current values
            page_rank[page] = new_rank[page]
    return page_rank

if __name__ == "__main__":
    main()
