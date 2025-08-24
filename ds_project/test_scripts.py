class Python:
        code_0 = """  
        rng = np.random.RandomState(1)
        """
        code_backup = """
        a = 5
        X = dataset.iloc[:, 1:a].values
        """

        error_code_1 = """
        rng = np.random.RandomState(1)
        """

        code_1 = """
            import numpy as np
            n_success = 0
            print("Python is great!")
            """

        code_2 = """
            import matplotlib
            import numpy as np
            import Casita.Papel as pape
            from sklearn.svm import SVC
            from sklearn.preprocessing import StandardScaler, Abuelito
            from sklearn.datasets import make_classification
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline
            X, y = make_classification(random_state=0)
            X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
            pipe = Pipeline([('scaler', StandardScaler()), ('svc', SVC())])
            # The pipeline can be used as any other estimator
            # and avoids leaking the test set into the train set
            pipe.fit(X_train, y_train)
            pipe.score(X_test, y_test)
            """

        code_3 = """
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            dataset = pd.read_csv('../input/Position_Salaries.csv')
            X = dataset.iloc[:, 1:2].values
            y = dataset.iloc[:, -1].values
            from sklearn.preprocessing import StandardScaler
            sc_X = StandardScaler()
            sc_Y = StandardScaler()
            X = sc_X.fit_transform(X)
            y = np.squeeze(sc_Y.fit_transform(y.reshape(-1, 1)))
            # the feature scaling will be done to both X and Y and still Y will remain the Vector
            from sklearn.svm import SVR
            regressor = SVR(kernel = 'rbf')
            regressor.fit(X, y)
            SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1,
                gamma='auto_deprecated', kernel='rbf', max_iter=-1, shrinking=True,
                tol=0.001, verbose=False)
            y_pred = regressor.predict([[6.5]])
            y_pred = sc_Y.inverse_transform(y_pred)
            print(y_pred)
            """

        code_4 = """
            from sklearn.preprocessing import StandardScaler
            X_scaled = StandardScaler().fit_transform(X)
            pca = decomposition.PCA(n_components=2)
            X_pca_scaled = pca.fit_transform(X_scaled)
            print('Projecting %d-dimensional data to 2D' % X_scaled.shape[1])
            plt.figure(figsize=(12,10))
            plt.scatter(X_pca_scaled[:, 0], X_pca_scaled[:, 1], c=df['diagnosis'], alpha=0.7, s=40);
            plt.colorbar()
            plt.title('PCA projection')
            plt.style.use('seaborn-muted');
        """
        code_5 = """
            # Import required libraries:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from sklearn import linear_model
        # Read the CSV file :
        data = pd.read_csv(“Fuel.csv”)
        data.head()
        # Let’s select some features to explore more :
        data = data[[“ENGINESIZE”,”CO2EMISSIONS”]]
        # ENGINESIZE vs CO2EMISSIONS:
        plt.scatter(data[“ENGINESIZE”] , data[“CO2EMISSIONS”] , color=”blue”)
        plt.xlabel(“ENGINESIZE”)
        plt.ylabel(“CO2EMISSIONS”)
        plt.show()
        # Generating training and testing data from our data:
        # We are using 80% data for training.
        train = data[:(int((len(data)*0.8)))]
        test = data[(int((len(data)*0.8))):]
        # Modeling:
        # Using sklearn package to model data :
        regr = linear_model.LinearRegression()
        train_x = np.array(train[[“ENGINESIZE”]])
        train_y = np.array(train[[“CO2EMISSIONS”]])
        regr.fit(train_x,train_y)
        # The coefficients:
        print (“coefficients : “,regr.coef_) #Slope
        print (“Intercept : “,regr.intercept_) #Intercept
        # Plotting the regression line:
        plt.scatter(train[“ENGINESIZE”], train[“CO2EMISSIONS”], color=’blue’)
        plt.plot(train_x, regr.coef_*train_x + regr.intercept_, ‘-r’)
        plt.xlabel(“Engine size”)
        plt.ylabel(“Emission”)
        # Predicting values:
        # Function for predicting future values :
        def get_regression_predictions(input_features,intercept,slope):
         predicted_values = input_features*slope + intercept
         return predicted_values
        # Predicting emission for future car:
        my_engine_size = 3.5
        estimatd_emission = get_regression_predictions(my_engine_size,regr.intercept_[0],regr.coef_[0][0])
        print (“Estimated Emission :”,estimatd_emission)
        # Checking various accuracy:
        from sklearn.metrics import r2_score
        test_x = np.array(test[[‘ENGINESIZE’]])
        test_y_ = np.array(test[[‘CO2EMISSIONS’]])
        test_y = regr.predict(test_x)
        print(“Mean absolute error: %.2f” % np.mean(np.absolute(test_y_ — test_y)))
        print(“Mean sum of squares (MSE): %.2f” % np.mean((test_y_ — test_y) ** 2))
        print(“R2-score: %.2f” % r2_score(test_y_ , test_y) )"""

        code_6 = """
               from sklearn.datasets import load_iris
        iris = load_iris()
        # Model (can also use single decision tree)
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=10)
        # Train
        model.fit(iris.data, iris.target)
        # Extract single tree
        estimator = model.estimators_[5]
        from sklearn.tree import export_graphviz
        # Export as dot file
        export_graphviz(estimator, out_file='tree.dot', 
                        feature_names = iris.feature_names,
                        class_names = iris.target_names,
                        rounded = True, proportion = False, 
                        precision = 2, filled = True)
        # Convert to png
        from subprocess import call
        call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])
        # Display in python
        import matplotlib.pyplot as plt
        plt.figure(figsize = (14, 18))
        plt.imshow(plt.imread('tree.png'))
        plt.axis('off');
        plt.show();
        """

        code_7 = """
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaler.fit(df_feat)
        df_scaled = scaler.transform(df_feat)
        df_scaled = pd.DataFrame(df_scaled,columns=df_feat.columns[:4])
        df_preprocessed = pd.concat([df_scaled,dummies,target],axis=1)
        df_preprocessed.head()
            """



        code_8 = """
        from sklearn.cluster import KMeans
        from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
        import matplotlib.pyplot as plt
        kmeans = KMeans(3,init='k-means++')
        #f = open("test.txt")
        plt.savefig("test")
        f.write("hi")
        kmeans.fit(df_preprocessed.drop('species',axis=1))
        print(confusion_matrix(df_preprocessed.species,kmeans.labels_))"""

        code_8_a = """
        from sklearn.cluster import KMeans
        from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
        kmeans = KMeans(4,init='k-means++')
        kmeans.fit(df_preprocessed.drop('species',axis=1))
        print(confusion_matrix(df_preprocessed.species,kmeans.labels_))"""

        code_8_b = """
        from sklearn.cluster import KMeans
        from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
        kmeans = KMeans(3,init='k-means++')
        kmeans.fit(df_preprocessed.drop('species',axis=1))
        Y = kmeans.predict([1, 2])
        print(confusion_matrix(df_preprocessed.species,kmeans.labels_))"""

        code_9 = """
            from sklearn.model_selection import train_test_split
        from sklearn.neighbors import KNeighborsClassifier
        # We need to split data for supervised learning models.
        X_train, X_test, y_train, y_test = train_test_split(df_preprocessed.drop('species',axis=1),target,test_size=0.50)
        knn = KNeighborsClassifier(n_neighbors=1)
        knn.fit(X_train,y_train)
        preds_knn = knn.predict(X_test)
        print(confusion_matrix(y_test,preds_knn))"""

        code_10 = """
            import pandas as pd
        df = pd.DataFrame([['green', 'M', 10.1, 'class1'],
                               ['red', 'L', 13.5, 'class2'],
                               ['blue', 'XL', 15.3, 'class1']])
        df.columns = ['color', 'size', 'price', 'classlabel']
        import numpy as np
        class_mapping = {label:idx for idx,label in 
                         enumerate(np.unique(df['classlabel']))}
        class_mapping
        """

        code_11 = """
        from sklearn.datasets import make_moons
        Xm, ym = make_moons(n_samples=100, noise=0.25, random_state=53)
        deep_tree_clf1 = DecisionTreeClassifier(random_state=42)
        deep_tree_clf2 = DecisionTreeClassifier(min_samples_leaf=4, random_state=42)
        deep_tree_clf1.fit(Xm, ym)
        deep_tree_clf2.fit(Xm, ym)
        fig, axes = plt.subplots(ncols=2, figsize=(10, 4), sharey=True)
        plt.sca(axes[0])
        plot_decision_boundary(deep_tree_clf1, Xm, ym, axes=[-1.5, 2.4, -1, 1.5], iris=False)
        plt.title("No restrictions", fontsize=16)
        plt.sca(axes[1])
        plot_decision_boundary(deep_tree_clf2, Xm, ym, axes=[-1.5, 2.4, -1, 1.5], iris=False)
        plt.title("min_samples_leaf = {}".format(deep_tree_clf2.min_samples_leaf), fontsize=14)
        plt.ylabel("")
        save_fig("min_samples_leaf_plot")
        plt.show()"""

        code_12 = """
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        p = 9
        q = 1
        model = SARIMAX(ts, order=(p,d,q))
        model_fit = model.fit(disp=1,solver='powell')
        fcast = model_fit.get_prediction(start=1, end=len(ts))
        ts_p = fcast.predicted_mean
        ts_ci = fcast.conf_int()
    """

        code_13 = """
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns; sns.set()
        rng = np.random.RandomState(1)
        X = np.dot(rng.rand(2, 2), rng.randn(2, 200)).T
        plt.scatter(X[:, 0], X[:, 1])
        plt.axis('equal')"""

        code_14 = """
        from sklearn.model_selection import cross_val_score
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        iris = load_iris()
        logreg = LogisticRegression()
        scores = cross_val_score(logreg, iris.data, iris.target)
        print("Cross-validation scores: {}".format(scores))
        """

        code_15 = """
        from sklearn.linear_model import LogisticRegression
        logisticRegr = LogisticRegression(solver = 'lbfgs')
        logisticRegr.fit(train_img, train_lbl)
        logisticRegr.predict(test_img[0].reshape(1,-1))
        logisticRegr.predict(test_img[0:10])
        predictions = logisticRegr.predict(test_img)
        """

        code_16 = """
        from sklearn.manifold import MDS
        model = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
        out = model.fit_transform(D)
        plt.scatter(out[:, 0], out[:, 1], **colorize)
        plt.axis('equal')
        """

        code_17 = """
        from sklearn.decomposition import PCA
        pca=PCA(n_components=2)
        pca.fit(X)
        X_pca=pca.transform(X)
        number_of_people=10
        index_range=number_of_people*10
        fig=plt.figure(figsize=(10,8))
        ax=fig.add_subplot(1,1,1)
        scatter=ax.scatter(X_pca[:index_range,0],
                    X_pca[:index_range,1], 
                    c=target[:index_range],
                    s=10,
                   cmap=plt.get_cmap('jet', number_of_people))
        ax.set_xlabel("First Principle Component")
        ax.set_ylabel("Second Principle Component")
        ax.set_title("PCA projection of {} people".format(number_of_people))
        fig.colorbar(scatter)"""

        code_18 = """
        from sklearn.model_selection import LeaveOneOut
        loo_cv=LeaveOneOut()
        clf=LinearDiscriminantAnalysis()
        cv_scores=cross_val_score(clf,
                                 X_pca,
                                 target,
                                 cv=loo_cv)
        print("{} Leave One Out cross-validation mean accuracy score:{:.2f}".format(clf.__class__.__name__, 
                                                                                    cv_scores.mean()))"""

        code_19 = """
        from sklearn.utils.fixes import signature
        step_kwargs = ({'step': 'post'}
                       if 'step' in signature(plt.fill_between).parameters
                       else {})
        plt.figure(1, figsize=(12,8))
        plt.step(recall['micro'], precision['micro'], color='b', alpha=0.2,
                 where='post')
        plt.fill_between(recall["micro"], precision["micro"], alpha=0.2, color='b',
                         **step_kwargs)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title(
            'Average precision score, micro-averaged over all classes: AP={0:0.2f}'
            .format(average_precision["micro"]))"""

        code_20 = """
        from sklearn.neighbors import KNeighborsClassifier
        from base import Base
        Xtrain, Xtest, ytrain, ytest = Base.clean_and_split()
        model = KNeighborsClassifier(n_neighbors=7)
        model.fit(Xtrain, ytrain)
        ypred = model.predict(Xtest)
        print("\n\nK-Nearest Neighbor Accuracy Score:", Base.accuracy_score(ytest, ypred), "%")"""

        code_21 = """
        import numpy as np # linear algebra
        import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
        import os
        
        for dirname, _, filenames in os.walk('/kaggle/input'):
            for filename in filenames:
                print(os.path.join(dirname, filename))"""

class R:
        code_1 = """
            library(ggplot2) # Data visualization
            library(readr) # CSV file I/O, e.g. the read_csv function
            library(sqldf)
            list.files("../input")
            print('Total runtime is ~2 mins')
            print('Importing train_2016 ... should be 90275')
            train_2016 <- read_csv("../input/train_2016_v2.csv", col_types = cols(transactiondate = col_skip(), parcelid = col_integer())); nrow(train_2016)
            print('Combining dupes (taking average) ... should be 90150')
            train_2016 <- sqldf('SELECT parcelid, avg(logerror) as logerror FROM train_2016 GROUP BY parcelid'); nrow(train_2016)
            print('Importing properties_2016 ... should be 2,985,217')
            properties_2016 <- read_csv("../input/properties_2016.csv", col_types = cols(parcelid = col_integer())); nrow(properties_2016)
            print('Combining train_2016 and properties_2016 ... should be 2,985,217')
            #alldata <- sqldf("SELECT * FROM properties_2016 LEFT JOIN train_2016 USING(parcelid)"); nrow(alldata)
            alldata <- merge(x = properties_2016, y = train_2016, by = "parcelid", all.x = TRUE)
            print('Building model ...')
            lr1 <- lm(logerror ~ fullbathcnt + calculatedfinishedsquarefeet + parcelid, data=alldata);
            summary(lr1) # view the model
            print('Making predictions ...')
            predictions <- data.frame(predict(lr1, alldata))
            print('Appending predictions to alldata ...')
            alldata$p_lr1 <- predictions$predict.lr1..alldata.
            alldata$p_lr1[is.na(alldata$p_lr1)] <- mean(alldata$logerror, na.rm = TRUE)  # Replace missing with average
            print('Average prediction value is ...')
            mean(alldata$p_lr1)
            print('Creating submission file')
            submit <- data.frame(alldata[,c("parcelid", "p_lr1")])
                          submit$"201610" <- round(submit$p_lr1,4)
                          submit$"201611" <- round(submit$p_lr1,4)
                          submit$"201612" <- round(submit$p_lr1,4)
                          submit$"201710" <- 0
                          submit$"201711" <- 0
                          submit$"201712" <- 0
            submit$p_lr1<- NULL # remove the original prediction from the submit file
            write.csv(submit, file = "submit_1.csv", row.names = FALSE, na="") # export the file for submission
            print('Done!')
            """

        code_2 = """
            library(tidyverse)
            list.files(path = "../input")
            #1-Import the data
            salary_data=read_csv("../input/salary-data-simple-linear-regression/Salary_Data.csv")
            #2-Summary and plot the data
            summary.data.frame(salary_data)
            plot(salary_data$YearsExperience,salary_data$Salary,xlab="Salary",ylab="Years of experience",main="Salary with respect to years of experience",col="blue")
            #3-Run the regression
            plot(salary_data$YearsExperience,salary_data$Salary, pch=16,cex=1.3, col="green",xlab="Years of experience",ylab="Salary",main="linear regression training set")
            lm=lm(Salary~YearsExperience,salary_data)
            summary(lm)
            abline(lm)
            plot(lm)
            """

        code_3 = """
        library(MASS)
        library(tidyverse)
        library(caret)
        all_data <- rbind(final_train[,-1],final_train_last[,-1],final_test[,-c(1,2)])
        preproc.param <- all_data %>% preProcess(method = c("center", "scale"))
        all_data.transformed <- preproc.param %>% predict(all_data)
        train.transformed <- all_data.transformed[1:15118,]
        validation.transformed <- all_data.transformed[15119:18717,]
        test.transformed <- all_data.transformed[18718:19717,]
        formule <- as.formula("accuracy_group~ accumulated_accuracy_group + dif_4070 + dif_2030 + duration_mean + dif_4030 + accumulated_uncorrect_attempts + Clip + + Chow_Time + somme_clip_game_activity + assessment_before_accuracy + accumulated_actions + acc_0 + acc_1 + acc_3 + acc_Bird + acc_Caul + acc_Mush + acc_Ches + acc_Cart + lgt_Caul + lgt_Mush + lgt_Ches + lgt_Cart + agt_Bird + agt_Caul + agt_Mush + agt_Ches + agt_Cart + ata_Bird + ata_Caul + ata_Mush + ata_Ches + ata_Cart + afa_Bird + afa_Caul + afa_Mush + afa_Ches + titre0 + titre1 + titre2 + titre3")
        model <- lda(formule, data = cbind(final_train[,1],train.transformed))"""

        code_4 = """
        install.packages("e1071")
        install.packages("caTools")
        install.packages("class")
        library(e1071)
        library(caTools)
        library(class)
        data(iris)
        head(iris)   
        split <- sample.split(iris, SplitRatio = 0.7)
        train_cl <- subset(iris, split == "TRUE")
        test_cl <- subset(iris, split == "FALSE")
        train_scale <- scale(train_cl[, 1:4])
        test_scale <- scale(test_cl[, 1:4])
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 1)
        classifier_knn
        cm <- table(test_cl$Species, classifier_knn)
        cm
        # Model Evaluation - Choosing K
        # Calculate out of Sample error
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 3
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 3)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 5
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 5)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 7
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 7)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 15
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 15)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 19
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 19)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
    """

        code_5 = """
        install.packages("caTools")    # For Logistic regression
        install.packages("ROCR")       # For ROC curve to evaluate model
        # Loading package
        library(caTools)
        library(ROCR) 
        # Splitting dataset
        split <- sample.split(mtcars, SplitRatio = 0.8)
        split
        train_reg <- subset(mtcars, split == "TRUE")
        test_reg <- subset(mtcars, split == "FALSE")
        # Training model
        logistic_model <- glm(vs ~ wt + disp, 
                              data = train_reg, 
                              family = "binomial")
        logistic_model
        # Summary
        summary(logistic_model)
        # Predict test data based on model
        predict_reg <- predict(logistic_model, 
                               test_reg, type = "response")
        predict_reg  
        # Changing probabilities
        predict_reg <- ifelse(predict_reg >0.5, 1, 0)
        # Evaluating model accuracy
        # using confusion matrix
        table(test_reg$vs, predict_reg)
        missing_classerr <- mean(predict_reg != test_reg$vs)
        print(paste('Accuracy =', 1 - missing_classerr))
        # ROC-AUC Curve
        ROCPred <- prediction(predict_reg, test_reg$vs) 
        ROCPer <- performance(ROCPred, measure = "tpr", 
                                     x.measure = "fpr")
        auc <- performance(ROCPred, measure = "auc")
        auc <- auc@y.values[[1]]
        auc
        # Plotting curve
        plot(ROCPer)
        plot(ROCPer, colorize = TRUE, 
             print.cutoffs.at = seq(0.1, by = 0.1), 
             main = "ROC CURVE")
        abline(a = 0, b = 1)
        auc <- round(auc, 4)
        legend(.6, .4, auc, title = "AUC", cex = 1)
        """

        code_6 = """
        library(dplyr)
        # Drop variables
        clean_titanic <- titanic % > %
        select(-c(home.dest, cabin, name, X, ticket)) % > % 
        #Convert to factor level
            mutate(pclass = factor(pclass, levels = c(1, 2, 3), labels = c('Upper', 'Middle', 'Lower')),
            survived = factor(survived, levels = c(0, 1), labels = c('No', 'Yes'))) % > %
        na.omit()
        glimpse(clean_titanic)"""

        code_7 = """
        ImpData <- as.data.frame(importance(rf.fit))
        ImpData$Var.Names <- row.names(ImpData)
        ggplot(ImpData, aes(x=Var.Names, y=`%IncMSE`)) +
          geom_segment( aes(x=Var.Names, xend=Var.Names, y=0, yend=`%IncMSE`), color="skyblue") +
          geom_point(aes(size = IncNodePurity), color="blue", alpha=0.6) +
          theme_light() +
          coord_flip() +
          theme(
            legend.position="bottom",
            panel.grid.major.y = element_blank(),
            panel.border = element_blank(),
            axis.ticks.y = element_blank()
          )
    """

        code_8 = """
            set.seed(123)
        valid_split <- initial_split(ames_train, .8)
        # training data
        ames_train_v2 <- analysis(valid_split)
        # validation data
        ames_valid <- assessment(valid_split)
        x_test <- ames_valid[setdiff(names(ames_valid), "Sale_Price")]
        y_test <- ames_valid$Sale_Price
        rf_oob_comp <- randomForest(
          formula = Sale_Price ~ .,
          data    = ames_train_v2,
          xtest   = x_test,
          ytest   = y_test
        )
        # extract OOB & validation errors
        oob <- sqrt(rf_oob_comp$mse)
        validation <- sqrt(rf_oob_comp$test$mse)
        # compare error rates
        tibble::tibble(
          `Out of Bag Error` = oob,
          `Test error` = validation,
          ntrees = 1:rf_oob_comp$ntree
        ) %>%
          gather(Metric, RMSE, -ntrees) %>%
          ggplot(aes(ntrees, RMSE, color = Metric)) +
          geom_line() +
          scale_y_continuous(labels = scales::dollar) +
          xlab("Number of trees")
      """

        code_9 = """
            IQ <- rnorm(40, 30, 2)
        # Sorting IQ level in ascending order
        IQ <- sort(IQ)
        # Generate vector with pass and fail values of 40 students
        result <- c(0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
        1, 0, 0, 0, 1, 1, 0, 0, 1, 0,
        0, 0, 1, 0, 0, 1, 1, 0, 1, 1,
        1, 1, 1, 0, 1, 1, 1, 1, 0, 1)
        # Data Frame
        df <- as.data.frame(cbind(IQ, result))
        # Print data frame
        print(df)
        # output to be present as PNG file
        png(file="LogisticRegressionGFG.png")
        # Plotting IQ on x-axis and result on y-axis
        plot(IQ, result, xlab = "IQ Level",
        ylab = "Probability of Passing")
        # Create a logistic model
        g = glm(result~IQ, family=binomial, df)
        # Create a curve based on prediction using the regression model
        curve(predict(g, data.frame(IQ=x), type="resp"), add=TRUE)
        # This Draws a set of points
        # Based on fit to the regression model
        points(IQ, fitted(g), pch=30)
        # Summary of the regression model
        summary(g)
        # saving the file
        dev.off()"""

        code_10 = """
        install.packages("quantreg")
        install.packages("ggplot2")
        install.packages("caret")
        # Loading the packages
        library(quantreg)
        library(dplyr)
        library(ggplot2)
        library(caret)
        # Model: Quantile Regression
        Quan_fit <- rq(disp ~ wt, data = mtcars)
        Quan_fit
        # Summary of Model
        summary(Quan_fit)
        # Plot
        plot(disp ~ wt, data = mtcars, pch = 16, main = "Plot")
        abline(lm(disp ~ wt, data = mtcars), col = "red", lty = 2)
        abline(rq(disp ~ wt, data = mtcars), col = "blue", lty = 2)"""

        code_11 = """
        library(tidyverse)
        library(caret)
        theme_set(theme_classic())
        # Load the data
        data("Boston", package = "MASS")
        # Split the data into training and test set
        set.seed(123)
        training.samples <- Boston$medv %>%
          createDataPartition(p = 0.8, list = FALSE)
        train.data  <- Boston[training.samples, ]
        test.data <- Boston[-training.samples, ]
        # Build the model
        model <- lm(medv ~ poly(lstat, 5, raw = TRUE),
                    data = train.data)
        # Make predictions
        predictions <- model %>% predict(test.data)
        # Model performance
        modelPerfomance = data.frame(
                            RMSE = RMSE(predictions, test.data$medv),
                             R2 = R2(predictions, test.data$medv)
                         )
        print(lm(medv ~ lstat + I(lstat^2), data = train.data))
        print(modelPerfomance)"""

        code_12 = """
            install.packages("caTools")    # For Logistic regression
            install.packages("ROCR")       # For ROC curve to evaluate model
        # Loading package
        library(caTools)
        library(ROCR) 
        # Splitting dataset
        split <- sample.split(mtcars, SplitRatio = 0.8)
        split
        train_reg <- subset(mtcars, split == "TRUE")
        test_reg <- subset(mtcars, split == "FALSE")
        # Training model
        logistic_model <- glm(vs ~ wt + disp, 
                              data = train_reg, 
                              family = "binomial")
        logistic_model
        # Summary
        summary(logistic_model)
        # Predict test data based on model
        predict_reg <- predict(logistic_model, 
                               test_reg, type = "response")
        predict_reg  
        # Changing probabilities
        predict_reg <- ifelse(predict_reg >0.5, 1, 0)
        # Evaluating model accuracy
        # using confusion matrix
        table(test_reg$vs, predict_reg)
        missing_classerr <- mean(predict_reg != test_reg$vs)
        print(paste('Accuracy =', 1 - missing_classerr))
        # ROC-AUC Curve
        ROCPred <- prediction(predict_reg, test_reg$vs) 
        ROCPer <- performance(ROCPred, measure = "tpr", 
                                     x.measure = "fpr")
        auc <- performance(ROCPred, measure = "auc")
        auc <- auc@y.values[[1]]
        auc
        # Plotting curve
        plot(ROCPer)
        plot(ROCPer, colorize = TRUE, 
             print.cutoffs.at = seq(0.1, by = 0.1), 
             main = "ROC CURVE")
        abline(a = 0, b = 1)
        auc <- round(auc, 4)
        legend(.6, .4, auc, title = "AUC", cex = 1)"""

        code_13 = """
            install.packages("dplyr")
        install.packages("glmnet")
        install.packages("ggplot2")
        install.packages("caret")
        # X and Y datasets
        X <- mtcars %>% 
             select(disp) %>% 
             scale(center = TRUE, scale = FALSE) %>% 
             as.matrix()
        Y <- mtcars %>% 
            select(-disp) %>% 
            as.matrix()
        # Model Building : Elastic Net Regression
        control <- trainControl(method = "repeatedcv",
                                      number = 5,
                                      repeats = 5,
                                      search = "random",
                                      verboseIter = TRUE)
        # Training ELastic Net Regression model
        elastic_model <- train(disp ~ .,
                                   data = cbind(X, Y),
                                   method = "glmnet",
                                   preProcess = c("center", "scale"),
                                   tuneLength = 25,
                                   trControl = control)
        elastic_model
        # Model Prediction
        x_hat_pre <- predict(elastic_model, Y)
        x_hat_pre
        # Multiple R-squared
        rsq <- cor(X, x_hat_pre)^2
        rsq
        # Plot
        plot(elastic_model, main = "Elastic Net Regression")"""

        code_14 = """
        cl<-makePSOCKcluster(5)
        registerDoParallel(cl)
        start.time<-proc.time()
        model<-train(target~., data=trainingset, method='rf')
        stop.time<-proc.time()
        run.time<-stop.time -start.time
        print(run.time)
        stopCluster(cl)"""

        code_15 = """
        # Installing Packages
        install.packages("e1071")
        install.packages("caTools")
        install.packages("class")
        # Loading package
        library(e1071)
        library(caTools)
        library(class)
        # Loading data
        data(iris)
        head(iris)
        # Splitting data into train
        # and test data
        split <- sample.split(iris, SplitRatio = 0.7)
        train_cl <- subset(iris, split == "TRUE")
        test_cl <- subset(iris, split == "FALSE")
        # Feature Scaling
        train_scale <- scale(train_cl[, 1:4])
        test_scale <- scale(test_cl[, 1:4])
        # Fitting KNN Model 
        # to training dataset
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 1)
        classifier_knn
        # Confusiin Matrix
        cm <- table(test_cl$Species, classifier_knn)
        cm
        # Model Evaluation - Choosing K
        # Calculate out of Sample error
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 3
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 3)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 5
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 5)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 7
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 7)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 15
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 15)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))
        # K = 19
        classifier_knn <- knn(train = train_scale,
                              test = test_scale,
                              cl = train_cl$Species,
                              k = 19)
        misClassError <- mean(classifier_knn != test_cl$Species)
        print(paste('Accuracy =', 1-misClassError))"""

        code_16 = """
        # Finding distance matrix
        distance_mat <- dist(mtcars, method = 'euclidean')
        distance_mat
        # Fitting Hierarchical clustering Model
        # to training dataset
        set.seed(240)  # Setting seed
        Hierar_cl <- hclust(distance_mat, method = "average")
        Hierar_cl
        # Plotting dendrogram
        plot(Hierar_cl)
        # Choosing no. of clusters
        # Cutting tree by height
        abline(h = 110, col = "green")
        # Cutting tree by no. of clusters
        fit <- cutree(Hierar_cl, k = 3 )
        fit
        table(fit)
        rect.hclust(Hierar_cl, k = 3, border = "green")"""

        code_17 = """
            library(ElemStatLearn)
        set = training_set
        #Building a grid of Age Column(X1)
        # and Estimated Salary(X2) Column
        X1 = seq(min(set[, 1]) - 1,
                 max(set[, 1]) + 1,
                 by = 0.01)
        X2 = seq(min(set[, 2]) - 1, 
                 max(set[, 2]) + 1, 
                 by = 0.01)
        grid_set = expand.grid(X1, X2)
        # Give name to the columns of matrix
        colnames(grid_set) = c('Age',
                               'EstimatedSalary')
        # Predicting the values and plotting
        # them to grid and labelling the axes
        y_grid = knn(train = training_set[, -3],
                     test = grid_set,
                     cl = training_set[, 3],
                     k = 5)
        plot(set[, -3],
             main = 'K-NN (Training set)',
             xlab = 'Age', ylab = 'Estimated Salary',
             xlim = range(X1), ylim = range(X2))
        contour(X1, X2, matrix(as.numeric(y_grid), 
                               length(X1), length(X2)),
                               add = TRUE)
        points(grid_set, pch = '.',
               col = ifelse(y_grid == 1, 
                            'springgreen3', 'tomato'))
        points(set, pch = 21, bg = ifelse(set[, 3] == 1, 
                                          'green4', 'red3'))"""

        code_18 = """
            install.packages("e1071")
        install.packages("caTools")
        install.packages("caret")
        # Loading package
        library(e1071)
        library(caTools)
        library(caret)
        # Splitting data into train
        # and test data
        split <- sample.split(iris, SplitRatio = 0.7)
        train_cl <- subset(iris, split == "TRUE")
        test_cl <- subset(iris, split == "FALSE")
        # Feature Scaling
        train_scale <- scale(train_cl[, 1:4])
        test_scale <- scale(test_cl[, 1:4])
        # Fitting Naive Bayes Model
        # to training dataset
        set.seed(120)  # Setting Seed
        classifier_cl <- naiveBayes(Species ~ ., data = train_cl)
        classifier_cl
        # Predicting on test data'
        y_pred <- predict(classifier_cl, newdata = test_cl)
        # Confusion Matrix
        cm <- table(test_cl$Species, y_pred)
        cm
        # Model Evaluation
        confusionMatrix(cm)"""

        code_19 = """
            install.packages('caTools')
        library(caTools)
        set.seed(123)
        split = sample.split(dataset$Purchased, SplitRatio = 0.75)
        training_set = subset(dataset, split == TRUE)
        test_set = subset(dataset, split == FALSE)"""

        code_20 = """
        dataset$Purchased = factor(dataset$Purchased,
                                   levels = c(0, 1))
        # Splitting the dataset into
        # the Training set and Test set
        # install.packages('caTools')
        library(caTools)
        set.seed(123)
        split = sample.split(dataset$Purchased,
                             SplitRatio = 0.75)
        training_set = subset(dataset, split == TRUE)
        test_set = subset(dataset, split == FALSE)
        # Feature Scaling
        training_set[-3] = scale(training_set[-3])
        test_set[-3] = scale(test_set[-3])
        # Fitting Decision Tree Classification
        # to the Training set
        # install.packages('rpart')
        library(rpart)
        classifier = rpart(formula = Purchased ~ .,
                           data = training_set)
        # Predicting the Test set results
        y_pred = predict(classifier,
                         newdata = test_set[-3],
                         type = 'class')
        # Making the Confusion Matrix
        cm = table(test_set[, 3], y_pred)"""


class Snakemake:
    code_1 = """rule samtools_index:
    input:
        "sorted_reads/{sample}.bam"
    output:
        "sorted_reads/{sample}.bam.bai"
    conda:
        "environment.yaml"
    shell:
        "samtools index {input}" """
