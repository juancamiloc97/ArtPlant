// Está es la configuración del servidor
const express = require('express')
const cors = require('cors')
var path = require('path'); // nos ayuda con el manejo de las rutas de los archivos
const nodemailer = require('nodemailer');

// configuración del servidor
const app = express()
const sqlite3 = require('sqlite3').verbose()
let sql

// Connection wth db

const db = new sqlite3.Database(path.resolve(__dirname, 'sensorData.db'),sqlite3.OPEN_READWRITE,(err) => {
  if(err) return console.error(err.message)
})

function saveData(data){
  sensorValue = data['sensorValue']
  if(sensorValue >= 2000){
    waterPump = 1
  }else{
    waterPump = 0
  }
  sql = `INSERT INTO sensors (temp,humidity, pressure, waterPump) values (0, 0, 0 ,${waterPump})`
  db.run(sql)
}

function sendEmail(data){
  console.log(data)
    var message = {
      from: "juancamilocano97@gmail.com",
      to: 'juancamilocano97@gmail.com',
      subject: "Informacion del estado de tu planta",
      text: data,
  };

  var transporter = nodemailer.createTransport({
      host:'smtp.gmail.com',
      port: 465,
      secure: true,
      service: 'gmail',
      auth: {
        user: 'juancamilocano97@gmail.com',
        pass: 'bqyvolagihcsyluo'
      }
  })

  transporter.sendMail(message, (error, info) => {
    if (error) {
        console.log("Error enviando email")
        console.log(error.message)
    } else {
        console.log("Email enviado")
    }
  })
}
//sql = `CREATE TABLE auth(id INTEGER PRIMARY KEY, esp32Id) `
//db.run(sql)
//// ip : res.send(id)
// ip : 192.168.0.114
//db.run('DROP TABLE auth ')
//http://192.168.0.114:8090/email

//insert data

//sql = `insert into users `


//app.use(express.static('programar'))
app.use(cors()) //nos ayuda a que no haya problemas con el origen de las aplicaciones que vana consumir las apis
app.use(express.json()) //nos permite configurar que la información que se puede recibir en el servidor, venga en formato json

// endpoint
app.get('/email',(req,res) =>{ // autenticar si esta actibo el esp \
    sendEmail({
      nombre:'camilo',
      apellido:'cano',
      mensaje:'Estoy enviando correos desde nodejs'
    })
    res.send({
      mensaje:"Email sent"
    })
})

app.get('/validate',(req,res) =>{ // autenticar si esta actibo el esp \
  datos = []
  sql = `SELECT esp32Id from AUTH`
  db.all(sql,[],(err,rows)=>{
    rows.forEach(row => {
      datos.push(row)
    });
    //console.log(datos)
    res.send(datos)
  })
})

app.post('/sensorsData',(req,res) =>{ // reibir datos
  var data = req.body
  console.log(data)
  saveData(data)
  console.log('received')
  sendEmail(`
    Hola soy Camilo, te quiero mostrar los datos del cuidado de tu orquidea
    humidity : ${data['humidity'] } %
    floor hunidity : ${data['floorHumidity']} %
    Temperature : ${data['temp']} ºC
    `)
  res.send({
    mensaje:'data received'
  })
})

//


app.listen(8090,()=>{
    console.log("Servidor escuchando...")
})
