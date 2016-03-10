app.controller('DocumentController', function ($scope, $http, $location, $routeParams) {
    /************************************************************************************************
     * Properties
     */
    $scope.doc_id = $routeParams.doc_id;

    $scope.model = {};
    $scope.keywords = [];
    $scope.corpora = [];
    $scope.closest = [];

    $scope.newCorpus = "";

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.onModelLoaded = function (data) {
        $scope.model = data;
        if ($scope.model == null) {
            $scope.model = {};
            return;
        }

        // Make the dates user-friendly
        $scope.model.scannedAsDate = new Date($scope.model.scanned).toLocaleString();
        $scope.model.createdAsDate = new Date($scope.model.dateCreated).toLocaleString();

        $scope.loadCorpora();
        $scope.request($scope.apiUrl + '/keywords', $scope.onKeywordsLoaded);
        $scope.request($scope.apiUrl + '/closest', $scope.onClosestLoaded);
    }

    $scope.onKeywordsLoaded = function (data) {
        $scope.keywords = data;
        if ($scope.keywords == null) {
            $scope.keywords = [];
            return;
        }
    }

    $scope.onCorpusLoaded = function (data) {
        $scope.corpora = data;
        if ($scope.corpora == null) {
            $scope.corpora = [];
            return;
        }
    }


    $scope.onClosestLoaded = function (data) {
        $scope.closest = data;
        if ($scope.closest == null) {
            $scope.closest = [];
            return;
        }
    }

    /************************************************************************************************
    * Actions
    */

    $scope.addCorpus = function () {
        var value = $scope.newCorpus.toLowerCase();
        $scope.newCorpus = "";

        if (value == "") {
            alert('Must specify a value!');
            return;
        }

        var matched = false;
        angular.forEach($scope.corpora, function (corpus) {
            if (corpus.title == value) {
                matched = true;
            }
        });
        if (matched) {
            alert('Already associated with ' + value);
            return;
        }

        var u = $scope.apiUrl + '/corpus';
        $http.post(u, {"name": value})
        .then(function (response) {
            $scope.loadCorpora()
        }, function (response) {
            alert(response.status)
        });
    };

    $scope.removeCorpus = function (url) {
        parts = url.split("/")
        id = parts[parts.length - 1];

        var title = id;
        angular.forEach($scope.corpora, function (corpus) {
            if (corpus.links[0].href.indexOf(url) != -1) {
                title = corpus.title;
            }
        });

        var answer = confirm("Remove the association to corpus '" + title + "'?\nThe corpus itself will not be deleted.");
        if (!answer)
            return;

        var u = $scope.apiUrl + '/corpus/' + id;
        $http.delete(u)
            .then(function (response) {
                $scope.loadCorpora()
            }, function (response) {
                alert(response.status)
            });
    };

    /************************************************************************************************
     * Methods
     */

    $scope.buildUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1' + $location.url()
        return url;
    };

    $scope.request = function (url, callback) {
        $http.get(url)
            .then(function (response) {
                callback(response.data)
            }, function (response) {
                alert(response.status)
            });
    }

    $scope.loadCorpora = function () {
        $scope.request($scope.apiUrl + '/corpus', $scope.onCorpusLoaded);
    };

    /************************************************************************************************
     * Initialization
     */

    $scope.apiUrl = $scope.buildUrl();

    $scope.keywordsUrl = $location.url() + '/keywords?limit=20'
    $scope.closestUrl = $location.url() + '/closest?limit=20'

    $scope.request($scope.apiUrl, $scope.onModelLoaded);
});