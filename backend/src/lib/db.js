import mongoose from "mongoose";

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("MongoDB connected successfully!", conn.connection.host);
  } catch (error) {
    console.error("Failed to connect to MongoDB", error.message);
    process.exit(1);  // Stop server if DB connection fails
  }
};

export default connectDB;
