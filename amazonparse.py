"""
    Amazon Parser
    Troy Rosenberg and Nkemdirim Dockery
    CIS4930

    -Title
    -Author(s)
    -Price
    -Current Price
    -Avg Review
    -Number of reviews
    -Items the customer also bought (w/ links)
    -Items frequently bought w/book (w/likes)
    -Format
    -Pages
    -Language
    -Publisher
    -Edition
    -Date Published
    -ISBN (10/13)
    -Product Dimensions
    -Shipping weight
    -Subjects
"""
from __future__ import print_function
from lxml import html
from lxml import etree
import re


class Parser(object):
    """This class represents the entire parsing functionality. The steps of
    the process are broken down into properties for modularity and
    easier access.
    """
    def __init__(self, in_line):
        self.source = html.parse(in_line).getroot()
        self.productDetails = self.getProductDetails()

    @property
    def title(self):
        """possible design refinement: break down node accesses by larger
            groups. author, format and title etc. are children of the same
            parent"""
        res = self.source.get_element_by_id("btAsinTitle").text
        return "Title: " + res.strip()

    @property
    def author(self):
        """author may be missing: 9780028631141.html
                    may be multiple:
                    may have dropdown list: """
        res = self.source.get_element_by_id("btAsinTitle").getparent() \
              .getparent()
        res = res.iterlinks()
        res_list = [link[0].text_content() for link in res]
        fmt_res = "Author(s): " + ", ".join(res_list)
        return fmt_res

    @property
    def type_(self):
        """Note that there are two methods for text .text and .text_content
        :( I havent seen any difference between them yet though. Note
        subelement accesss starts from zero"""
        res = self.source.get_element_by_id("btAsinTitle")[0].text_content()
        return res.strip("[]")

    def getProductDetails(self):
        """
        Create a list containing the product details
        """
        tmpList = []
        for elem in self.source.xpath(".//h2"):
            if elem.text == 'Product Details':
                currNode = elem.getparent()
                for li in currNode.xpath(".//li"):
                    tmpList.append(li)
                return tmpList   
        return("None")

    @property
    def language(self):
        """
        Use the Product details list to
        find the language
        """
        for elem in self.productDetails:
            if( elem.text_content().find("Language") != -1):
                return(elem.text_content().split(':')[1].strip()) 
        return("None")

    @property
    def pages(self):
        """
        Uses the Product Details list to
        find the pages
        """
        for elem in self.productDetails:
            if( elem.text_content().find("page") != -1):
                return(elem.text_content().split(':')[1].split(' ')[1].strip()) 
        return("None")


    @property
    def edition(self):
        """
        Use the Product Details list to
        find the book's edition
        """
        for elem in self.productDetails:
#edition is under published info, find this li first
#cannot search on edition or will pick up kindle
            if( elem.text_content().find("Publisher") != -1):
                edLoc = elem.text_content().find("ed")
                if( edLoc != -1 ):
                    semiLoc = elem.text_content()[:edLoc].find(';')
                    return(elem.text_content()[semiLoc+1:edLoc].strip())
        return("None")


    @property
    def date(self):
        """
        Use the Product Details list to
        find the book's edition
        """
        for elem in self.productDetails:
#date is under published info, find this li first
            if( elem.text_content().find("Publisher") != -1):
                openLoc = elem.text_content().find("(")
                if( openLoc != -1 ):
                    closeLoc = elem.text_content().find(')')
                    return(elem.text_content()[openLoc+1:closeLoc].strip())
        return("None")


    @property
    def isbn10(self):
        """
        Use the Product Details to
        find the book's ISBN10
        NOTE*****: most kindle seem to have
        an ASIN which is 10, should I make that
        the kindle isbn10????
        """
        for elem in self.productDetails:
            if(elem.text_content().find("ISBN-10") != -1):
                return(elem.text_content().split(':')[1].strip())
        return("None")


    @property
    def isbn13(self):
        """
        Use the Product Details to
        find the book's ISBN13
        """
        for elem in self.productDetails:
            if(elem.text_content().find("ISBN-13") != -1):
                return(elem.text_content().split(':')[1].strip())
        return("None")

    
    @property
    def publisher(self):
        """
        Use the Prodcut Details to
        find the book's publisher
        """
        for elem in self.productDetails:
            if(elem.text_content().find("Publisher") != -1):
#If there is an endtion the published will come bfore the ';'
                if(elem.text_content().find(';') != -1):
                    return(elem.text_content().split(':')[1][:elem.text_content().split(':')[1].find(';')].strip())
#other wise it comes before (date)
                elif(elem.text_content().find('(') != -1):
                    return(elem.text_content().split(':')[1][:elem.text_content().split(':')[1].find('(')].strip())
                else:
                    return("None")
        return("None")


    @property
    def dimensions(self):
        """
        Use the Product Details to
        find the book's dimentions
        """
#kindle books do not have dimensions,
#if its kindle dont waste time
        if(self.type_ != 'Kindle Edition'): 
            for elem in self.productDetails:
                if(elem.text_content().find("Product Dimensions") != -1):
                    return(elem.text_content().split(':')[1].strip())
            return("None")
        return("None")


    @property 
    def weight(self):
        """
        Use the product details to
        find the book's weight
        """
#kindle books do not have weight,
#if its kindle dont waste time
        if(self.type_ != 'Kindle Edition'): 
            for elem in self.productDetails:
                if(elem.text_content().find("Shipping Weight") != -1):
                    return(elem.text_content().split(':')[1][:elem.text_content().split(':')[1].find('(')].strip())
            return("None")
        return("None")


    @property
    def subjects(self):
        """
        Parse for the book's subjects
        """
        subsList = []
        for elem in self.source.xpath(".//h2"):
            if elem.text == "Look for Similar Items by Subject":
                currNode = elem.getparent()
                for li in currNode.xpath(".//label"):
                    subsList.append(li.text_content())
                return subsList
        return("None")





if __name__ == "__main__":
    import doctest
    doctest.testfile("test.txt")

##url = "http://www.amazon.com/Algorithm-Design-Manual-Steven-Skiena/dp/
##1849967202/ref=sr_1_1?s=books&ie=UTF8&qid=1294839612&sr=1-1 "
##doc = html.parse(url).getroot()
##print (doc.find_class("parseasinTitle")[0].get_element_by_id("btAsinTitle"))

##class Book(object):
##    """
##    spam = Parser("
##    """
##    def __init__(self, data):
##
##select count(type) from sqlite_master where type='table' and
##    name='TABLE_NAME_TO_CHECK';


#create the re to find ed or edition
#"""
#pattern = re.compile(r'''
#                (?<init> \s*)
#                (?P<publisher> \w+)
#                (?<edition> \d)
#                [(]
#                (?<date> \w)
#                [)]
#                ''', re.MULTILINE | re.DOTALL | re.VERBOSE)
#temp = pattern.search(elem.text_content())
#print(temp.group('edition'))
#"""
