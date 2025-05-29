const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { GoogleSpreadsheet } = require('google-spreadsheet');
require('dotenv').config();

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

client.on('qr', (qr) => qrcode.generate(qr, { small: true }));

client.on('ready', async () => {
  console.log('✅ WhatsApp Bot is ready!');

  async function checkAndSendMessages() {
    const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID);
    await doc.useServiceAccountAuth({
      client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\n/g, '\n'),
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

  // Run immediately
  await checkAndSendMessages();

  // Repeat every 7 minutes (420,000 ms)
  setInterval(checkAndSendMessages, 420000);
});

client.initialize();
