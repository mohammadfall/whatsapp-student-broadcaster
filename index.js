const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { GoogleSpreadsheet } = require('google-spreadsheet');
require('dotenv').config();

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: { headless: true, args: ['--no-sandbox'] }
});

client.on('qr', qr => qrcode.generate(qr, { small: true }));
client.on('ready', async () => {
  console.log('✅ WhatsApp client is ready');

  const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID);
  await doc.useServiceAccountAuth({
    client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
  });
  await doc.loadInfo();
  const sheet = doc.sheetsByIndex[0];
  const rows = await sheet.getRows();

  for (let row of rows) {
    if (row.Status !== '✅') {
      const number = row.Phone.replace(/[^0-9+]/g, '');
      try {
        await client.sendMessage(`${number}@c.us`, row.Message);
        row.Status = '✅';
        await row.save();
        console.log(`✅ Sent to ${number}`);
      } catch (err) {
        console.error(`❌ Failed for ${number}`, err.message);
      }
    }
  }
});

client.initialize();
