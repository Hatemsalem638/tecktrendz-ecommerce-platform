const Feature = require("../../models/Feature");

// Add a new feature image
const addFeatureImage = async (req, res) => {
  try {
    const { image } = req.body;
    console.log(image, "image");

    const featureImages = new Feature({ image });
    await featureImages.save();

    res.status(201).json({
      success: true,
      data: featureImages,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      success: false,
      message: "Some error occurred!",
    });
  }
};

// Get all feature images
const getFeatureImages = async (req, res) => {
  try {
    const images = await Feature.find({});
    res.status(200).json({
      success: true,
      data: images,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      success: false,
      message: "Some error occurred!",
    });
  }
};

// Delete a feature image by its URL
const deleteFeatureImage = async (req, res) => {
  try {
    const { imageUrl } = req.body;

    const deletedImage = await Feature.findOneAndDelete({ image: imageUrl });

    if (!deletedImage) {
      return res.status(404).json({
        success: false,
        message: "Image not found",
      });
    }

    res.status(200).json({
      success: true,
      message: "Feature image removed successfully",
    });
  } catch (error) {
    console.log(error);
    res.status(500).json({
      success: false,
      message: "Error occurred while removing the image",
    });
  }
};

module.exports = {
  addFeatureImage,
  getFeatureImages,
  deleteFeatureImage,
};
