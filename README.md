<div align="center">

# E-commerce Performance Analysis and Optimization
#### **Team Campus Security**

_"Protecting your e-commerce success, just as Campus Security protects NUS"_

</div>



## About The Project

E-commerce has transformed the way we shop, offering convenience and access to a broad range of products and services. However, the industry faces several challenges, including fluctuating demand, inventory management, pricing optimization, and user experience enhancement. With numerous data points generated from transactions, user interactions, and product performance, there are ample opportunities for optimization and analysis.

Our project, **E-commerce Performance Analysis and Optimization**, aims to address these challenges through data-driven insights and provide an in-depth analysis of key areas for improvement. By leveraging various datasets and analytical techniques, we focus on identifying trends, optimizing operations, and proposing actionable insights to enhance overall e-commerce performance.


## Getting Started
Follow these instructions to set up and run the project on your local machine using Docker.

### Prerequisites

1. **Docker**: Make sure Docker is installed and running on your computer. [Install Docker](https://docs.docker.com/get-docker/) if you haven't already.
2. **Input Data Folder**: Download the `input` data folder from Google Drive:
   - [Google Drive Link](https://drive.google.com/drive/folders/1sz4cY5a2JpFrcXni-9ORfn1vDuE4_p9K)
3. **Output Folder**: Create an empty folder named `output` in the project root directory.

### Installation

1.  Navigate to Directory that you want the project repository to be
2.  **Clone the Repository**: Run the following command to clone this repository:
   ```bash
   git clone https://github.com/robbiechia/Campus-Security.git
   ```
3. **Set Up Environment Variables**:
  * Open the Cloned Repository in Visual Studio Code (VS Code).
  * Open the `.env` file
  * Update the `INPUT_DIR` and `OUTPUT_DIR` variables to match the paths of your `input` and `output` folders, respectively.
  * Save the `.env` file.

4. **Navigate to Project Directory**
   ```bash
   cd Campus-Security
   ```

### Running the Application

1. **Build the Docker Containers**
   ```bash
      docker-compose build
   ```
2. **Run the Application**
   * To start all Modules: 
      ```bash
         docker-compose up
      ```
   * To start a specific module only, replace `<module_name>` with the name of the desired modul: 
      ```bash
         docker-compose up <module_name>
      ```

### Example: Run a Specific Module (eg. Delivery Optimization )

1. **Modify Variables in `.env` File**
   - Update the `ORDER_DATE_OF_INTEREST` variable to the next day.
   - Set `NUM_VEHICLES` (ideally no more than 4).
   - Adjust the `VEHICLE_CAPACITY` as needed.

2. **Update Input and Output Directories**
   - Ensure the correct `Input` and `Output` directories are specified in the `.env` file.

3. **Save the `.env` File**
   - Once changes are made, save the `.env` file to apply the updates.

4. **Start the Module**

   To run the delivery module, use the following command:

   ```bash
   docker-compose run order_fulfillment_process
   ```

5. **Monitor the Execution**
    - Watch the process as it runs, monitoring logs and progress in the terminal.

6. **Check New Output**
    - After the module completes, check the new output file generated for the specific date in the `Output` Folder.


### Modules Available
- `data_preparation_subgroup_a`
- `customer_reviews_sentiment_analysis_module`
- `customer_behaviour_analysis_module`
- `customer_churn_analysis_module`
- `marketing_analysis_module`
- `data_preparation_subgroup_b`
- `pricing_strategy_module`
- `inventory_management`
- `order_fulfillment_process`
- `dashboarding_module`


### Next Steps 
* Refer to [Wiki](https://github.com/robbiechia/Campus-Security/wiki#campus-security-e-commerce-performance-analysis-and-optimization) for further instructions



## Acknowledgements 
We would like to thank Professor Hernandez Marin Sergio and our fellow Teaching Assistants for their guidance and support throughout the development of this project.
We also appreciate the feedback given by fellow coursemates during the roadshow.
