from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hey"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>&#161Hola</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<html><body>"
                output += "<h3><a href='/restaurants/new'>Create new Restaurant</a></h3>"

                for restaurant in restaurants:
                    output += "%s<br>" % restaurant.name
                    output += "<a href='/restaurants/%s/edit'>Edit</a><br>" % restaurant.id
                    output += "<a href='/restaurants/%s/delete'>Delete</a><br><br>" % restaurant.id

                output += "</body></html>"

                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Create new Restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="newRestaurantName" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"

                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):

                restaurantId = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()

                output = ""
                output += "<html><body>"
                output += "<h1>%s</h1>" % restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><input name="editRestaurant" type="text" ><input type="submit" value="Submit"> </form>''' % restaurantId
                output += "</body></html>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):

                restaurantId = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()

                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?</h1>" % restaurant.name
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'><input type="submit" value="Yes"><a href='/restaurants'><input type="button" value="No"></a></form>''' % restaurantId
                output += "</body></html>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            print("PATH: %s" % self.path)
            if self.path.endswith("/restaurants/new"):
                print("Saving new restaurant")
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('newRestaurantName')
                    newRestaurant = Restaurant(name=messageContent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

                return

            if self.path.endswith("/edit"):
                print("editing restaurant")
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('editRestaurant')

                    restaurantId = self.path.split('/')[2]
                    print("Restaurant ID: %s" % restaurantId)
                    restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
                    print("Restaurant name: %s" % restaurant.name)
                    restaurant.name = messageContent[0]
                    session.add(restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

                return

            if self.path.endswith("/delete"):
                print("deleting restaurant")

                restaurantId = self.path.split('/')[2]
                print("Restaurant ID: %s" % restaurantId)
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
                print("Restaurant name: %s" % restaurant.name)
                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                return

        except:
            print("Error")
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server is running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()