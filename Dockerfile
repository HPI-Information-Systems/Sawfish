FROM ubuntu:22.04
RUN apt-get update -y && apt-get install -y openjdk-11-jdk maven wget unzip
RUN mkdir /app && mkdir /app/sawfish && mkdir /app/sawfish/src && mkdir /app/metanome
COPY pom.xml /app/sawfish
COPY src /app/sawfish/src
RUN wget -O /app/metanome.zip "https://hpi.de/fileadmin/user_upload/fachgebiete/naumann/projekte/repeatability/DataProfiling/Metanome/deployment-1.2-SNAPSHOT-package_with_tomcat.zip" && unzip /app/metanome.zip -d /app/metanome
WORKDIR /app/sawfish
RUN mvn install && mv target/sawfish-1.1-SNAPSHOT.jar /app/metanome/backend/WEB-INF/classes/algorithms
WORKDIR /app/metanome
EXPOSE 8080
EXPOSE 8081
CMD ["/bin/sh", "run.sh"]