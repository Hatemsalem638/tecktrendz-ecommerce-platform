const paypal = require('paypal-rest-sdk');

paypal.configure({
  'mode': 'sandbox', 
  'client_id': 'AYwktpOe695RWj_qlCRYz9AK44EuCuBLsyOW3j5U-8N8chZXH7vXC8PRou3DtnhuCC78GzK5pjrMrCUc',
  'client_secret': 'EOARQvLuWbm6rAD0oKWGHqnqOLPx3TF86oQ0WIaJjpPIS7jvy6egK4m_GgKw_6WTc3M2WThgubFkuh7k'
});


module.exports = paypal;