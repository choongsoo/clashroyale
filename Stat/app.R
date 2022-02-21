library(shiny)

server <- function(input, output, session) {}

# simply packages a legit web app into a shiny app
shinyApp(ui = htmlTemplate("www/app.html"), server)
