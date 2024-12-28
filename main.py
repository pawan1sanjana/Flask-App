from kivy.app import App
from kivy.uix.webview import WebView

class FlaskWebApp(App):
    def build(self):
        # Create a WebView to load your Flask app
        webview = WebView()
        # Replace with your Flask app's URL
        webview.url = "https://flask-app-git-main-pawan1sanjanas-projects.vercel.app/>"
        return webview

if __name__ == '__main__':
    FlaskWebApp().run()
