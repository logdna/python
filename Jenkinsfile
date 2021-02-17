library 'magic-butler-catalogue'
def PROJECT_NAME = 'logdna-python'
def TRIGGER_PATTERN = ".*@logdnabot.*"

pipeline {
  agent none

  options {
    timestamps()
    ansiColor 'xterm'
  }

  triggers {
    issueCommentTrigger(TRIGGER_PATTERN)
  }

  stages {
    stage('Test') {
      agent {
        docker {
          image "us.gcr.io/logdna-k8s/python:3.7-ci"
          customWorkspace "${PROJECT_NAME}-${BUILD_NUMBER}"
        }
      }

      environment {
        XDG_CONFIG_HOME = pwd()
        POETRY_VIRTUALENV_IN_PROJECT = true
      }

      steps {
        sh 'poetry config --list --local'
        sh 'poetry install --no-interaction -vvv'
        sh 'poetry run task lint'
        sh 'poetry run task test'
      }

      post {
        always {
          junit 'coverage/test.xml'
          publishHTML target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'coverage',
            reportFiles: 'index.html',
            reportName: "coverage-${BUILD_TAG}"
          ]
        }
      }
    }

    stage('Release') {
      when {
        tag pattern: "[0-9]+\\.[0-9]+\\.[0-9]+", comparator: "REGEXP"
      }

      agent {
        docker {
          image "us.gcr.io/logdna-k8s/python:3.7-ci"
          customWorkspace "${PROJECT_NAME}-${BUILD_NUMBER}"
        }
      }
      steps {
        witCredentials([
          usernamePassword(
            credentialsId: 'pypi-username-password',
            usernameVariable: 'TWINE_USERNAME',
            passwordVariable: 'TWINE_PASSWORD'
          )
        ]){
          sh 'python setup.py sdist'
          sh 'twine upload dist/logdna-*.tar.gz'
        }
      }
    }
  }
}
