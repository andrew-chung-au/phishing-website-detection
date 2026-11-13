# Phishing Websites Features

**Rami M. Mohammad**  
School of Computing and Engineering  
University of Huddersfield  
Huddersfield, UK.  
rami.mohammad@hud.ac.uk  

**Fadi Thabtah**  
E-Business Department  
Canadian University of Dubai  
Dubai, UAE.  
fadi@cud.ac.ae  

**Lee McCluskey**  
School of Computing and Engineering  
University of Huddersfield  
Huddersfield, UK.  
t.l.mccluskey@hud.ac.uk  

---

One of the challenges faced by our research was the unavailability of reliable training datasets. In fact, this challenge faces any researcher in the field. However, although plenty of articles about predicting phishing websites using data mining techniques have been disseminated these days, no reliable training dataset has been published publicly, maybe because there is no agreement in literature on the definitive features that characterize phishing websites, hence it is difficult to shape a dataset that covers all possible features. 

In this article, we shed light on the important features that have proved to be sound and effective in predicting phishing websites. In addition, we proposed some new features, experimentally assign new rules to some well-known features and update some other features.

---

## 1. Address Bar based Features

### Using the IP Address
If an IP address is used as an alternative of the domain name in the URL, such as “http://125.98.3.123/fake.html”, users can be sure that someone is trying to steal their personal information. Sometimes, the IP address is even transformed into hexadecimal code as shown in the following link “http://0x58.0xCC.0xCA.0x62/2/paypal.ca/index.html”.  
**Rule:** IF ...

### Long URL to Hide the Suspicious Part
Phishers can use long URL to hide the doubtful part in the address bar. For example:  
`http://federmacedoadv.com.br/3f/aze/ab51e2e319e51502f416dbe46b773a5e/?cmd=_home&dispatch=11004d58f5b74f8dc1e7c2e8dd4105e811004d58f5b74f8dc1e7c2e8dd4105e8@phishing.website.html`

To ensure accuracy of our study, we calculated the length of URLs in the dataset and produced an average URL length. The results showed that if the length of the URL is greater than or equal 54 characters then the URL classified as phishing. By reviewing our dataset we were able to find 1220 URLs lengths equals to 54 or more which constitute 48.8% of the total dataset size.  
**Rule:** IF ...

### Using URL Shortening Services “TinyURL”
URL shortening is a method on the “World Wide Web” in which a URL may be made considerably smaller in length and still lead to the required webpage. This is accomplished by means of an “HTTP Redirect” on a domain name that is short, which links to the webpage that has a long URL. For example, the URL “http://portal.hud.ac.uk/” can be shortened to “bit.ly/19DXSk4”.  
**Rule:** IF ...

### URL’s having “@” Symbol
Using “@” symbol in the URL leads the browser to ignore everything preceding the “@” symbol and the real address often follows the “@” symbol.  
**Rule:** IF ...

### Redirecting using “//”
The existence of “//” within the URL path means that the user will be redirected to another website. An example of such URLs is: “http://www.legitimate.com//http://www.phishing.com”. We examine the location where the “//” appears. We find that if the URL starts with “HTTP”, that means the “//” should appear in the sixth position. However, if the URL employs “HTTPS” then the “//” should appear in seventh position.  
**Rule:** IF ...

### Adding Prefix or Suffix Separated by (-) to the Domain
The dash symbol is rarely used in legitimate URLs. Phishers tend to add prefixes or suffixes separated by (-) to the domain name so that users feel that they are dealing with a legitimate webpage. For example `http://www.Confirme-paypal.com/`.  
**Rule:** IF ...

### Sub Domain and Multi Sub Domains
Let us assume we have the following link: `http://www.hud.ac.uk/students/`. A domain name might include the country-code top-level domains (ccTLD), which in our example is “uk”. The “ac” part is shorthand for “academic”, the combined “ac.uk” is called a second-level domain (SLD) and “hud” is the actual name of the domain. To produce a rule for extracting this feature, we firstly have to omit the (www.) from the URL which is in fact a sub domain in itself. Then, we have to remove the (ccTLD) if it exists. Finally, we count the remaining dots. If the number of dots is greater than one, then the URL is classified as “Suspicious” since it has one sub domain. However, if the dots are greater than two, it is classified as “Phishing” since it will have multiple sub domains. Otherwise, if the URL has no sub domains, we will assign “Legitimate” to the feature.  
**Rule:** IF ...

### HTTPS (Hyper Text Transfer Protocol with Secure Sockets Layer)
The existence of HTTPS is very important in giving the impression of website legitimacy, but this is clearly not enough. The authors in (Mohammad, Thabtah and McCluskey 2012; Mohammad, Thabtah and McCluskey 2013) suggest checking the certificate assigned with HTTPS including the extent of the trust certificate issuer, and the certificate age. Certificate Authorities that are consistently listed among the top trustworthy names include: “GeoTrust, GoDaddy, Network Solutions, Thawte, Comodo, Doster and VeriSign”. Furthermore, by testing out our datasets, we find that the minimum age of a reputable certificate is two years.  
**Rule:** IF ...

### Domain Registration Length
Based on the fact that a phishing website lives for a short period of time, we believe that trustworthy domains are regularly paid for several years in advance. In our dataset, we find that the longest fraudulent domains have been used for one year only.  
**Rule:** IF ...

### Favicon
A favicon is a graphic image (icon) associated with a specific webpage. Many existing user agents such as graphical browsers and newsreaders show favicon as a visual reminder of the website identity in the address bar. If the favicon is loaded from a domain other than that shown in the address bar, then the webpage is likely to be considered a Phishing attempt.  
**Rule:** IF ...

### Using Non-Standard Port
This feature is useful in validating if a particular service (e.g. HTTP) is up or down on a specific server. In the aim of controlling intrusions, it is much better to merely open ports that you need. Several firewalls, Proxy and Network Address Translation (NAT) servers will, by default, block all or most of the ports and only open the ones selected. If all ports are open, phishers can run almost any service they want and as a result, user information is threatened. The most important ports and their preferred status are shown in Table 1.  
**Rule:** IF ...

**Table 1: Common ports to be checked**

| PORT | Service | Meaning | Preferred Status |
| :--- | :--- | :--- | :--- |
| 21 | FTP | Transfer files from one host to another | Close |
| 22 | SSH | Secure File Transfer Protocol | Close |
| 23 | Telnet | Provide a bidirectional interactive text-oriented communication | Close |
| 80 | HTTP | Hyper test transfer protocol | Open |
| 443 | HTTPS | Hypertext transfer protocol secured | Open |
| 445 | SMB | Providing shared access to files, printers, serial ports | Close |
| 1433 | MSSQL | Store and retrieve data as requested by other software applications | Close |
| 1521 | ORACLE | Access oracle database from web. | Close |
| 3306 | MySQL | Access MySQL database from web. | Close |
| 3389 | Remote Desktop | Allow remote access and remote collaboration | Close |

### The Existence of “HTTPS” Token in the Domain Part of the URL
The phishers may add the “HTTPS” token to the domain part of a URL in order to trick