CONTAINER_NAME="my-tf-container"
IMAGE_NAME="my-tf-image"
HOST_DIR="$PWD/src"
CONTAINER_DIR="/src"

if [ $(docker ps -a | grep $CONTAINER_NAME | wc -l) -eq 1 ]; then
    echo "Container $CONTAINER_NAME already exists. Executing \"$*\" in it."
    docker exec -it $CONTAINER_NAME $*
else
    read -p "Do you want to remove the container after it is done? (Y/n) " rm_yes
    if [ "$rm_yes" != "y" ]; then
        REMOVE="--rm"
    else
        REMOVE=""
    fi

    read -p "Do you want to expose port 6006? (y/N) " expose_yes
    if [ "$expose_yes" = "y" ]; then
        PORT="-p 6006:6006"
    else
        PORT=""
    fi

    docker run -it $PORT $REMOVE --gpus all --name $CONTAINER_NAME -v $HOST_DIR:$CONTAINER_DIR -w $CONTAINER_DIR $IMAGE_NAME "$*"
fi
