import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests
import DataFetch


def create_article_html(article, content_template):
    new_article = BeautifulSoup(str(content_template), "html.parser")

    # Set the title and make it a hyperlink
    title = new_article.find('h2')
    title_link = new_article.new_tag('a', href=article['article_url'])
    title_link.string = article['article_title'][:300]
    title.clear()
    title.append(title_link)

    # Set the subtitle/content in the p tag with class 'subtitle'
    subtitle = new_article.find('p', class_='subtitle')
    subtitle.string = article['content'][:200] + "..."

    # Remove the "Read more" link if it exists
    link = new_article.find('a')
    if link and link.string == "Read more":
        link.decompose()

    return str(new_article).strip()



def make_email(news, research):
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the template path using current directory
    template_path = os.path.join(current_dir, 'New_email.html')

    # Load the template HTML
    with open(template_path, 'r', encoding='utf-8') as template_file:
        soup = BeautifulSoup(template_file.read(), "html.parser")

    # Extract the header and footer
    header = soup.find('div', class_='newsletter-header')
    footer = soup.find('div', class_='newsletter-footer')

    # Extract content templates for Research and News sections
    research_section = soup.find('div', class_='newsletter-content')
    news_section = research_section.find_next('div', class_='newsletter-content')

    # Extract CSS styles
    css = str(soup.head.style)

    # Initialize the newsletter content
    research_content = ""
    news_content = ""

    enigma_news_content = DataFetch.fetch_enigma_news()

    enigma_news_content = enigma_news_content[0]
    # print(enigma_news_content)

    # Populate research content
    for article in research:
        research_content += create_article_html(article, research_section)

    # Populate news content
    for article in news:
        news_content += create_article_html(article, news_section)

    # Format the final email content
    email_content = f"""
    <!DOCTYPE html>
  <html>
    <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css" />
    <style>
      {css}
    </style>
    </head>
    <body>
    <section class="section">
      <div class="column is-half center-align">
      <!-- Header -->
      <div class="newsletter-header" style="background-color: #7449D6; color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="left" style="padding: 0; margin: 0; vertical-align: middle;">
          <h1 style="font-size: 2rem; margin: 0;">The Weekly Epoch</h1>
          <p style="font-size: 1rem; margin: 0; margin-top: 5px;">by Enigma ♡</p>
          </td>
          <td align="right" style="padding: 0; margin: 0; text-align: right; vertical-align: middle;">
          <!--
          <img
            src="https://i.postimg.cc/nzkZW3xv/mascots.png"
            alt="Header Image"
            style="max-width: 100px; height: auto; display: block; margin: 0 auto;"
          />
          -->
          </td>
        </tr>
        </table>
      </div>

       <!-- Enigma News Section
      <div class="newsletter-content center-align">
        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse;">
        <tr>
          <td style="padding: 0.5rem; text-align: center;">
          <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; width: 100%;">
            <tr>
            <td style="width: 100%; text-align: center; vertical-align: middle;">
              <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; display: inline-block; width: auto;">
              <tr>
                <td style="border-top: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              <tr>
                <td style="padding: 0.5rem 1rem; text-align: center;">
                <h2 style="margin: 0; padding: 0; font-size: 20px; line-height: 1.2;">Whats New At Enigma</h2>
                </td>
              </tr>
              <tr>
                <td style="border-bottom: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              </table>
            </td>
            </tr>
          </table>
          </td>
        </tr>
        
        <tr>
          <td style="text-align: center;">
          {enigma_news_content['news']['body']}
          </td>
        </tr>
      
        </table>
      </div>
      -->

      <!-- Latest Research Section -->
      <div class="newsletter-content center-align">
        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse;">
        <tr>
          <td style="padding: 0.5rem; text-align: center;">
          <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; width: 100%;">
            <tr>
            <td style="width: 100%; text-align: center; vertical-align: middle;">
              <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; display: inline-block; width: auto;">
              <tr>
                <td style="border-top: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              <tr>
                <td style="padding: 0.5rem 1rem; text-align: center;">
                <h2 style="margin: 0; padding: 0; font-size: 20px; line-height: 1.2;">Latest Research</h2>
                </td>
              </tr>
              <tr>
                <td style="border-bottom: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              </table>
            </td>
            </tr>
          </table>
          </td>
        </tr>
        <tr>
          <td style="text-align: center;">
          {research_content}
          </td>
        </tr>
        </table>
      </div>

      <!-- Latest News Section -->
      <div class="newsletter-content center-align">
        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse;">
        <tr>
          <td style="padding: 0.5rem; text-align: center;">
          <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; width: 100%;">
            <tr>
            <td style="width: 100%; text-align: center; vertical-align: middle;">
              <table align="center" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; display: inline-block; width: auto;">
              <tr>
                <td style="border-top: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              <tr>
                <td style="padding: 0.5rem 1rem; text-align: center;">
                <h2 style="margin: 0; padding: 0; font-size: 20px; line-height: 1.2;">News</h2>
                </td>
              </tr>
              <tr>
                <td style="border-bottom: 1px solid #000; width: 100%; height: 0;"></td>
              </tr>
              </table>
            </td>
            </tr>
          </table>
          </td>
        </tr>
        <tr>
          <td style="text-align: center;">
          {news_content}
          </td>
        </tr>
        </table>
      </div>

       

      <!-- Horizontal Line -->
      <hr class="footer-line" />

      <!-- Banner Section 
      <div class="banner-section" style="text-align: center;">
        <img
        src="https://i.postimg.cc/nhg97QYV/Enigma-Email-Banner-V1.png"
        alt="Enigma Banner"
        class="banner-image"
        style="display: block; margin: 0 auto; max-width: 100%;"
        />
      </div>
      -->
      <!-- Footer -->
      <div class="newsletter-footer center-align" style="padding: 0.5rem; text-align: center;">
        <p>Stay connected with us!</p>
        <a href="https://enigma.iiitkottayam.ac.in/unsubscribe" style="color: #3273dc; font-weight: bold; text-decoration: none;">Unsubscribe</a> |
        <a href="https://enigma.iiitkottayam.ac.in/contact" style="color: #3273dc; font-weight: bold; text-decoration: none;">Contact Us</a> |
        <a href="https://enigma.iiitkottayam.ac.in/subscribe" style="color: #3273dc; font-weight: bold; text-decoration: none;">Subscribe Now</a>
      </div>
      </div>
    </section>
    </body>
  </html>

    """

    # Save the email content to an output file
    output_path = os.path.join(current_dir, 'output_email.html')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(email_content)

    return email_content


def send_email(email: str, content: str):
    try:
        # Define the URL
        url = "https://script.google.com/macros/s/AKfycbwpsXLCmxF7VMq_KA1NW0mJkiH-way5y1ijuF9qPPTkZh2A4Aa88pBzzM-PXFaEVN55/exec"
        
        # Set up query parameters
        params = {
            'email': email
        }

        # Prepare headers and body
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'content': content
        }

        # Send the POST request
        response = requests.post(url, headers=headers, params=params, json=data)

        # Parse and return response
        if response.status_code == 200:
            result = response.json()
            print("Email sent successfully:", result)
            return {"message": "Email sent successfully", "result": result}
        else:
            print("Failed to send email:", response.text)
            return {"error": "Failed to send email", "status_code": response.status_code}

    except Exception as error:
        # Handle any exceptions
        print("Error sending email:", error)
        return {"error": "An error occurred while sending email"}

