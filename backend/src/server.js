import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import connectDB from "./lib/db.js";
import uploadRoutes from "./routes/upload.js";

dotenv.config();
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// DB Connection
await connectDB();

// Routes
app.use("/api", uploadRoutes);

// Start server
<<<<<<< HEAD
const PORT = process.env.PORT || 8001;
=======
const PORT = process.env.PORT || 8000;
>>>>>>> 597ccf41dd54ec10daf12d0a71636f27cedcd518
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
