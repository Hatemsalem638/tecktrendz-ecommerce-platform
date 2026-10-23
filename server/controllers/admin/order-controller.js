const Order = require("../../models/Order");
const fs = require("fs");
const path = require("path");

const getAllOrdersOfAllUsers = async (req, res) => {
  try {
    const orders = await Order.find({});

    if (!orders.length) {
      return res.status(404).json({
        success: false,
        message: "No orders found!",
      });
    }

    res.status(200).json({
      success: true,
      data: orders,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      success: false,
      message: "Some error occured!",
    });
  }
};

const getOrderDetailsForAdmin = async (req, res) => {
  try {
    const { id } = req.params;

    const order = await Order.findById(id);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: "Order not found!",
      });
    }

    res.status(200).json({
      success: true,
      data: order,
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      success: false,
      message: "Some error occured!",
    });
  }
};

const updateOrderStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { orderStatus } = req.body;

    const order = await Order.findById(id);

    if (!order) {
      return res.status(404).json({
        success: false,
        message: "Order not found!",
      });
    }

    await Order.findByIdAndUpdate(id, { orderStatus });

    const filePath = path.join(__dirname, "../../orders.txt");

    fs.readFile(filePath, "utf8", (err, data) => {
      if (err) return console.error("Failed to read orders.txt:", err);

      const updatedLines = data
        .split("\n")
        .map((line) => {
          if (line.startsWith(`Order ID: ${id},`)) {
            return `Order ID: ${id}, Status: ${orderStatus}`;
          }
          return line;
        })
        .join("\n");

      fs.writeFile(filePath, updatedLines, (err) => {
        if (err) console.error("Failed to update order status in file:", err);
        else console.log("Order status updated in orders.txt");
      });
    });

    res.status(200).json({
      success: true,
      message: "Order status is updated successfully!",
    });
  } catch (e) {
    console.log(e);
    res.status(500).json({
      success: false,
      message: "Some error occured!",
    });
  }
};

module.exports = {
  getAllOrdersOfAllUsers,
  getOrderDetailsForAdmin,
  updateOrderStatus,
};