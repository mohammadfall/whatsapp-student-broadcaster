const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const { GoogleSpreadsheet } = require('google-spreadsheet');
const fs = require('fs');
const path = require('path');
require('dotenv').config();
const express = require('express');
const { google } = require('googleapis');

const app = express();
const PORT = process.env.PORT || 3000;

// 🟢 Express basic routes
app.get('/', (req, res) => res.send('🚀 WhatsApp Bot is Live on Railway!'));
app.get('/qr', (req, res) => {
  const qrPath = path.join(__dirname, 'qr.png');
  res.sendFile(qrPath);
});
app.listen(PORT, () => console.log(`🚀 Express server running on port ${PORT}`));

// 🟢 WhatsApp client
const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

// 🟢 QR Code + Upload to Drive
client.on('qr', async (qr) => {
  const qrFilePath = path.join(__dirname, 'qr.png');
  try {
    await qrcode.toFile(qrFilePath, qr);
    console.log('📸 QR code saved to qr.png - افتح /qr في المتصفح');

    await uploadToDrive(qrFilePath);
  } catch (err) {
    console.error('❌ Failed to generate or upload QR', err);
  }
});

// 🟢 Upload to Google Drive
async function uploadToDrive(filePath) {
  const auth = new google.auth.GoogleAuth({
    credentials: {
      type: 'service_account',
      project_id: process.env.GOOGLE_PROJECT_ID,
      private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
      client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    },
    scopes: ['https://www.googleapis.com/auth/drive'],
  });

  const drive = google.drive({ version: 'v3', auth });

  const fileMetadata = {
    name: 'qr.png',
    parents: ['1KbNbzytTYcCvpSozhUgoUcFVIxDlf9K2'], // 🟢 Your folder ID
  };

  const media = {
    mimeType: 'image/png',
    body: fs.createReadStream(filePath),
  };

  try {
    const response = await drive.files.create({
      resource: fileMetadata,
      media: media,
      fields: 'id',
    });
    console.log(`✅ QR uploaded to Drive: https://drive.google.com/file/d/${response.data.id}/view`);
  } catch (err) {
    console.error('❌ Error uploading to Google Drive:', err);
  }
}

// 🟢 Ready event
client.on('ready', async () => {
  console.log('✅ WhatsApp Bot is ready!');
  await checkAndSendMessages();
  setInterval(checkAndSendMessages, 7 * 60 * 1000);
});

// 🟢 Message sender
async function checkAndSendMessages() {
  const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID);
  await doc.useServiceAccountAuth({
    client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    private_key: JSON.parse(`"${process.env.GOOGLE_PRIVATE_KEY}"`),
  });

  await doc.loadInfo();
  const sheet = doc.sheetsByIndex[0];
  const rows = await sheet.getRows();

  for (let row of rows) {
    if (row.Status !== '✅') {
      const number = row.Phone.replace(/[^0-9+]/g, '');
      const message = row.Message;
      try {
        await client.sendMessage(`${number}@c.us`, message);
        console.log(`✅ Sent to ${number}`);
        row.Status = '✅';
        await row.save();
      } catch (err) {
        console.error(`❌ Failed for ${number}`, err);
      }
    }
  }
}

client.initialize();
