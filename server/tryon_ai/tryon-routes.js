const express = require('express');
const multer = require('multer');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const axios = require('axios');
const Product = require('../models/Product');

const router = express.Router();

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'tryon_ai/uploads/');
  },
  filename: function (req, file, cb) {
    const ext = path.extname(file.originalname);
    cb(null, 'user_image' + ext);
  }
});

const upload = multer({ storage: storage });

router.post('/', upload.single('userImage'), async (req, res) => {
  const productId = req.body.productId;

  if (!req.file || !productId) {
    return res.status(400).json({ success: false, message: 'Missing image or productId' });
  }

  try {
    const product = await Product.findById(productId);
    if (!product || !product.image) {
      return res.status(404).json({ success: false, message: 'Product not found or missing image' });
    }

    const productImageUrl = product.image;
    const imageName = path.basename(productImageUrl); 
    const productImagePath = path.join(__dirname, '..', 'tryon_ai', 'cp-vton', 'data', 'product_images', imageName);

    if (!fs.existsSync(productImagePath)) {
      const response = await axios.get(productImageUrl, { responseType: 'stream' });
      const writer = fs.createWriteStream(productImagePath);
      response.data.pipe(writer);

      await new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
      });
    }

    const userImagePath = path.join(__dirname, '..', 'tryon_ai', 'uploads', req.file.filename);

    const pythonCmd = `python tryon_ai/tryon_runner.py "${userImagePath}" "${productImagePath}"`;
    exec(pythonCmd, (error, stdout, stderr) => {
      if (error) {
        console.error('Python error:', stderr);
        return res.status(500).json({ success: false, message: 'Try-on failed', error: stderr });
      }

      console.log('Python output:', stdout);
      res.json({
        success: true,
        outputImage: 'tryon_result.jpg',
      });
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: 'Unexpected server error' });
  }
});

module.exports = router;
