# Install required packages
install.packages("readx1")
install.packages("netmeta")
install.packages("gemtc")
install.packages("rstan")
install.packages("igraph")
install.packages("tidyr")
install.packages("rjags")
install.packages("BUGSnet")
install.packages("viridis")

# Load the packages
library(netmeta)
library(rstan)
library(igraph)
##이거만 해도 됨.
library(readxl)
library(gemtc)
library(tidyr)
library(dplyr)
library(ggplot2)
library(viridis)

# Load the Excel file
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "EAD")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "PNF")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "NAS")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "TBC")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "HAT")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "MC")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "Retransplantation")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "ACR")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "RRT")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "1ygl")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "1ypd")

data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "NAS_singledual")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "TBC_singledual")

data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "EAD_shortlong_HOPE")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "EAD_shortlong_NMP")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "MC_shortlong_HOPE")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "MC_shortlong_NMP")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "NAS_shortlong_HOPE")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "NAS_shortlong_NMP")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "TBC_shortlong_HOPE")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "TBC_shortlong_NMP")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "PNF_shortlong_HOPE")
data <- read_excel("C:/R_liverMP_exceldata/ECD_RoB.xlsx", sheet = "RRT_shortlong_HOPE")


# Preview the data
head(data)

# Summarize the total sample size for each treatment group
treatment_sample_sizes <- data %>%
  group_by(treatment) %>%
  summarise(totalSampleSize = sum(sampleSize, na.rm = TRUE))

# Convert data to gemtc format
network_b_bin <- mtc.network(data.ab = data,  
                             description = "Bayesian Hierarchical Model for NMA")



#set colours for the rest of the analyses
vertex_colors_MP <- c("#4472C4",
                      "#4472C4",
                      "black")

vertex_colors_MP <- c("#4472C4",
                      "red",
                      "black")


vertex_colors_MP <- c("red",
                      "red",
                      "black")

vertex_colors_MP <- c("slateblue2",
                      "black",
                      "skyblue2")

vertex_colors_MP <- c("darkred",
                      "black",
                      "pink")

vertex_colors_MP <- c("navy",
                      "black",
                      "yellow")

#generate a network plot
plot(network_b_bin, 
     vertex.color = vertex_colors_MP,
     vertex.size = (treatment_sample_sizes$totalSampleSize)/6,
     vertex.label.cex = 1,
     show.legend = FALSE,
     vertex.label.color = "white"
         )
######
vertex.label.family = "Arial",
vertex.label.color = "white",
vertex.label.size = 8,
edge.width = "weight*2", # Edge width by weight
show.legend = FALSE
#######

summary(network_b_bin) 
print(network_b_bin)

# 네트워크 모델 설정
model_b_bin_fe <- mtc.model(network_b_bin, linearModel='fixed', n.chain = 4) # fixed
model_b_bin_re <- mtc.model(network_b_bin, linearModel='random', n.chain = 4) # random

# MCMC simulation
### burn-in 5000, iteration 10000, thin 20 ########
# Fixed
mcmc_b_bin_fe <- mtc.run(model_b_bin_fe, n.adapt=40000, n.iter=110000, thin=20)
# Random
mcmc_b_bin_re <- mtc.run(model_b_bin_re, n.adapt=40000, n.iter=110000, thin=20)

# 검증
summary(mcmc_b_bin_fe)
summary(mcmc_b_bin_re)

# Plots
plot(mcmc_b_bin_fe)
gelman.plot(mcmc_b_bin_fe)
gelman.diag(mcmc_b_bin_fe) 

plot(mcmc_b_bin_re)
gelman.plot(mcmc_b_bin_re)
gelman.diag(mcmc_b_bin_re) 


# [Residual Deviance] Create a data frame for ggplot2
deviance_MP <- mtc.deviance(mcmc_b_bin_fe)

dev_df <- data.frame(
  Study = rownames(deviance_MP$dev.ab),       # Study names
  MeanDeviance = deviance_MP$dev.ab  # Mean deviance values
)

dev_df$MeanDeviance_avg <- (dev_df$MeanDeviance.1 + dev_df$MeanDeviance.2) / 2

ggplot(dev_df, aes(x = Study, y = MeanDeviance_avg)) +
  geom_point(size = 3, color = "black") +
  geom_segment(aes(x = Study, xend = Study, y = 0, yend = MeanDeviance_avg), color = "black", linewidth=1) +
  labs(title = "", 
       x = "", 
       y = "Residual Deviance") +
  theme_minimal() +
  theme(
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "gray90"),
    panel.grid.minor = element_line(color = "gray90", linetype = "dotted"),
    axis.text.x = element_text(angle = 90, hjust = 1)
  )




###(Skip) Inconsistency 가정 확인: node-splitting을 통해서, closed loop이여야함!! SCS vs HOPE vs NMP 모조리 있어야함######## 
#mtc.nodesplit에 네트워크 셋업을 넣는다.
#fixed model node
split_b_bin_fe <- mtc.nodesplit(network_b_bin, linearModel='fixed', n.adapt=5000, n.iter=10000, thin=10)
#random model node
split_b_bin_re <- mtc.nodesplit(network_b_bin, linearModel='random', n.adapt=5000, n.iter=10000, thin=5)


######Treatment ranking
#Calculate the rank data
ranks_b_bin_fe <- rank.probability(mcmc_b_bin_fe, preferredDirection = -1)

#convert our rank data into a plottable format
rank_pos <- c()
rank_prob <- c()
for(i in 1:length(network_b_bin$treatments$id)){
  rank_pos <- c(rank_pos, rep(i, length(network_b_bin$treatments$id)))
  rank_prob <- c(rank_prob, ranks_b_bin_fe[,i])
}

#generate a dataframe to store the rank data
df_rank_plot_b_bin <- data.frame(Probability = rank_prob,
                                treatment_old = network_b_bin$treatments$id,
                                Treatment = network_b_bin$treatments$description,
                                Rank = factor(rank_pos))

#change the Treatment to a factor variable
#this is so that we can order the different treatments in the plot in the order we want
#here we are ordering treatments alphabetically and then by increasing dosage
df_rank_plot_b_bin$Treatment <- factor(df_rank_plot_b_bin$Treatment, 
                                    levels = df_rank_plot_b_bin$Treatment[c(1,3,2)])


#generate the rankogram
rank_HOPENMP_plot <- ggplot(df_rank_plot_b_bin, aes(x=Treatment, y=Probability, fill=Rank))+
  geom_bar(stat="identity", color="black", position=position_dodge())+
  scale_fill_grey(start=0, end=1) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust=1))+
  xlab("")
  ylab("")

rank_HOPENMP_plot

print(ranks_b_bin_fe)



##########FOREST PLOT############
#extract the summary information where we calculate the mean difference relative to SCS
summary_SCS <- summary(relative.effect(mcmc_b_bin_fe, t1 = "SCS"))
summary_SCS
df_forest_SCS <- data.frame(Treatment = network_b_bin$treatments$description,
                            colours = vertex_colors_MP,
                            Mean = NA,
                            CrI_Lower = NA,
                            CrI_Upper = NA)

#remove any data corresponding to the placebo treatment from our dataframe
df_forest_SCS <- subset(df_forest_SCS, Treatment != "SCS")

#calculate the dimensions of our dataframe - this is to shorten the code later
dim_df <- dim(df_forest_SCS )[1]

#Extract mean values for the estimate of the effect of each treatment
df_forest_SCS$Mean <- summary_SCS$summaries$statistics[1:dim_df]

#Extract lower bounds for the credible intervals of each treatment effect
df_forest_SCS$CrI_Lower <- summary_SCS$summaries$quantiles[1:dim_df]

#Extract upper bounds for the credible intervals of each treatment effect
df_forest_SCS$CrI_Upper <- summary_SCS$summaries$quantiles[((4*dim_df)+1):(5*dim_df)]

#change the Treatment to a factor variable
#this is so that we can order the different treatments in the plot in the order we want
#here we are ordering treatments in same order as Langford et al. (2020)
df_forest_SCS$Treatment <- factor(df_forest_SCS$Treatment, 
                                         levels = df_forest_SCS$Treatment[c(1,2,3)])
#generate our forest plot for placebo comparisons
forest_SCS_plot <- ggplot(df_forest_SCS, aes(x=Mean, 
                                                           y=Treatment,
                                                           fill = Treatment)) +
  geom_errorbar(aes(y = Treatment, xmin=CrI_Lower, xmax=CrI_Upper, width = 0)) + 
  geom_point(size = 5, shape = 21, color = "black") +
  scale_fill_manual(values = df_forest_SCS$colours[c(1,2,3)]) +
  theme_classic() +
  theme(legend.position = "none") +
  xlab("") +
  ylab("")+
  geom_vline(colour = "gray50", xintercept = 0, linetype="dashed") +
  scale_y_discrete(limits=rev)


forest_SCS_plot


## vs NMP
summary_SCS <- summary(relative.effect(mcmc_b_bin_fe, t1 = "Short_term"))
summary_SCS

###Forest plot (단순)
forest(relative.effect(mcmc_b_bin_fe, t1="SCS"), digits=2)
forest(relative.effect(mcmc_b_bin_fe, t1="Short_term"), digits=3)


###total samplesize for each treatment####
library(readxl)

# Specify the file path
file_path <- "C:/R_liverMP_exceldata/ECD_RoB.xlsx"

# List of sheets to process
sheets <- c("EAD", "PNF", "NAS", "TBC", "HAT", "MC", 
            "Retransplantation", "ACR", "RRT", "1ygl", "1ypd",
            "NAS_singledual", "TBC_singledual",
            "EAD_shortlong_HOPE", "EAD_shortlong_NMP", 
            "MC_shortlong_HOPE", "MC_shortlong_NMP", 
            "NAS_shortlong_HOPE", "NAS_shortlong_NMP", 
            "TBC_shortlong_HOPE", "TBC_shortlong_NMP", 
            "PNF_shortlong_HOPE", "RRT_shortlong_HOPE")

# Initialize a list to store results
results <- list()

# Loop through each sheet
for (sheet in sheets) {
  # Read the data from the sheet
  data <- read_excel(file_path, sheet = sheet)
  
  # Calculate total sampleSize for each treatment
  treatment_totals <- aggregate(sampleSize ~ treatment, data = data, sum)
  
  # Store the results with the sheet name
  results[[sheet]] <- treatment_totals
}

# Display results for each sheet
for (sheet in names(results)) {
  cat("\nSheet:", sheet, "\n")
  print(results[[sheet]])
}

# Optional: Combine all results into a single data frame for summary
combined_results <- do.call(rbind, lapply(names(results), function(sheet) {
  cbind(Sheet = sheet, results[[sheet]])
}))

# Print combined results
print(combined_results)
