library(shiny)

# simply packages a legit web app into a shiny app
shinyApp(ui = htmlTemplate("www/app.html"), server = function(input, output, session) {})
