# Lab session # 7: Using the Elastic Stack to study scraped data from a web page
### Task 7.3: Study the obtained data using the Elastic Stack

#### Q73: Take a screenshot of the Kibana Dashboard showing the above plots without filters. Set a couple of filters, take screetshots. Add all the screenshots to the Lab7 folder of your answers repository.
#### Q74: Explain what you have done in the README.md file of the Lab7 folder of your answers repository, add the new plot. Push the code changes to your scrapy-lab repository

1. A tag cloud showing who are the most popular actors for the period. A new record is inserted every time that an actor participates in a movie, therefore, you can count how many records exist for each actor.
![Chart1](img/popular_actors2.png)

2. A bar diagram showing how many actors employ each movie. Take the 50 movies with more actors for the period.
![Chart2](img/movie_actor2.png)

3. A bard diagram showing the filming activity for each year (plot the total count of records per year).
![Chart3](img/movie_year.png)

4. Finally for the custom question we chose to scrape IMDb to identify the most successful movies in the 21st century in terms of financial terms. In other words, we plot the profit for each movie (percentage) based on the budget spent in its production and its world cumulative gross. For this purpose we wrote a new parsing function `parse_movie` which parses the movie's IMDB page before scraping the actors' pages from the movie credits' page.

#### Q75: How long have you been working on this session? What have been the main difficulties you have faced and how have you solved them?

We have worked approximately 10 hours each for this session, mainly in order to get acquinted with scrapy. Scraping IMDb and debugging scrapy e.g. realise that the domain name should not be included in the redirection links, took most of our time. Getting started with elastic and kibana was pretty easy with the provided package. 
